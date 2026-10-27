#!/usr/bin/env python3
"""Gera data.json a partir do CSV exportado do Google Forms.

Uso:
    python3 build_data.py [caminho do CSV]

O CSV é procurado automaticamente no diretório quando o caminho não é informado.
Somente contagens agregadas são gravadas: timestamps, consentimentos e
respostas abertas individuais não entram no data.json.
"""

import csv
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TOKEN_RE = re.compile(r"[\wÀ-ÿ]+")
MIN_TOKEN_LEN = 3

STOPWORDS = {
    "acredito", "ainda", "algo", "até", "cada", "com", "como", "dados", "das",
    "deve", "dos", "eles", "entre", "então", "esse", "esses", "fazer", "forma",
    "iria", "isso", "mais", "maneira", "mas", "mesmo", "meus", "muitas",
    "muito", "não", "para", "pela", "pode", "por", "que", "resposta",
    "respostas", "sem", "ser", "seria", "seu", "seus", "sobre", "sua", "suas",
    "também", "tem", "uma", "usar", "uso", "utilizar", "você",
}

# Frases recorrentes escolhidas para exibição. Os rótulos são fixos e as
# contagens são recalculadas a partir das respostas.
PHRASE_LABELS = {
    "pergunta10": [
        "escolas públicas", "sala de aula", "inteligência artificial",
        "formação docente", "uso pedagógico",
    ],
    "pergunta22": [
        "pensamento crítico", "sala de aula", "inteligência artificial",
    ],
}

PAPEL_PROFESSOR_OPTIONS = [
    "Orientar o uso crítico e responsável da IA como ferramenta pedagógica",
    "Integrar a IA nas atividades, mas sempre com supervisão e debate",
    "Proibir o uso de IA durante as aulas para evitar fraudes",
]

CATEGORICAL_COLUMNS = [
    ("curso", "1."),
    ("semestre", "2."),
    ("faixaEtaria", "3."),
    ("genero", "4."),
    ("acessoInternet", "5."),
    ("formacaoIA", "6."),
    ("conhecimentoDiretrizes", "7."),
    ("classificacaoRiscos", "8."),
    ("mediacaoHumana", "9."),
    ("preparacaoCurso", "16."),
    ("riscoEtico", "20."),
    ("desumanizacao", "21."),
    ("regrasInstitucionais", "19."),
    ("disciplinasIA", "18."),
]

LIKERT_COLUMNS = [
    ("formacaoDocenteIA", "11."),
    ("beneficiosIA", "12."),
    ("substituicaoProfessor", "13."),
    ("questionarIA", "14."),
    ("preparoPessoal", "15."),
]

OPEN_COLUMNS = [
    ("pergunta10", "10."),
    ("pergunta22", "22."),
]


def find_csv(explicit_path=None):
    if explicit_path:
        path = Path(explicit_path)
        if not path.is_file():
            sys.exit("CSV não encontrado: {}".format(path))
        return path
    candidates = sorted(BASE_DIR.glob("*.csv"))
    if not candidates:
        sys.exit("Nenhum CSV encontrado em {}".format(BASE_DIR))
    if len(candidates) > 1:
        sys.exit("Mais de um CSV encontrado; informe o caminho desejado.")
    return candidates[0]


def find_column(headers, prefix):
    matches = [h for h in headers if h.startswith(prefix)]
    if len(matches) != 1:
        sys.exit("Coluna ambígua ou ausente para o prefixo {!r}".format(prefix))
    return matches[0]


def count_items(rows, column, keep_zero=False):
    """Contagens ordenadas por frequência; empates na ordem de primeira aparição."""
    counter = Counter()
    for row in rows:
        value = (row.get(column) or "").strip()
        if value:
            counter[value] += 1
    ordered = sorted(counter.items(), key=lambda item: -item[1])
    return [
        {"label": label, "value": value}
        for label, value in ordered
        if keep_zero or value > 0
    ]


def count_scale(rows, column):
    """Escalas 1-5 em ordem crescente; níveis sem resposta são omitidos."""
    counter = Counter()
    for row in rows:
        value = (row.get(column) or "").strip()
        if value:
            counter[value] += 1
    return [
        {"label": label, "value": counter[label]}
        for label in sorted(counter, key=lambda item: int(item))
    ]


def tokenize(text):
    return TOKEN_RE.findall(text.lower())


def word_counts(rows, column):
    counter = Counter()
    for row in rows:
        for token in tokenize(row.get(column) or ""):
            if len(token) >= MIN_TOKEN_LEN and token not in STOPWORDS:
                counter[token] += 1
    return counter


def top_words(rows, column, limit=45):
    ordered = sorted(word_counts(rows, column).items(), key=lambda item: -item[1])
    return [
        {"label": word, "value": count}
        for word, count in ordered[:limit]
    ]


def phrase_count(rows, column, phrase):
    parts = phrase.split()
    total = 0
    for row in rows:
        tokens = tokenize(row.get(column) or "")
        total += sum(
            tokens[start:start + len(parts)] == parts
            for start in range(len(tokens) - len(parts) + 1)
        )
    return total


def main():
    csv_path = find_csv(sys.argv[1] if len(sys.argv) > 1 else None)
    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        headers = reader.fieldnames

    consent_column = headers[1]
    consented = [
        row for row in rows
        if (row.get(consent_column) or "").strip().upper().startswith("SIM")
    ]
    if len(consented) != len(rows):
        print(
            "Aviso: {} resposta(s) sem consentimento foram ignoradas.".format(
                len(rows) - len(consented)
            )
        )
    rows = consented

    columns = {prefix: find_column(headers, prefix) for _, prefix in CATEGORICAL_COLUMNS + LIKERT_COLUMNS + OPEN_COLUMNS}
    papel_column = find_column(headers, "17.")

    data = {
        "n": len(rows),
        "generatedAt": date.today().isoformat(),
        "categorical": {
            key: count_items(rows, columns[prefix])
            for key, prefix in CATEGORICAL_COLUMNS
        },
        "likert": {
            key: count_scale(rows, columns[prefix])
            for key, prefix in LIKERT_COLUMNS
        },
        "papelProfessor": sorted(
            (
                {"label": option, "value": sum(option in (row.get(papel_column) or "") for row in rows)}
                for option in PAPEL_PROFESSOR_OPTIONS
            ),
            key=lambda item: -item["value"],
        ),
        "wordclouds": {},
    }

    for key, prefix in OPEN_COLUMNS:
        column = columns[prefix]
        answers = [row for row in rows if (row.get(column) or "").strip()]
        data["wordclouds"][key] = {
            "words": top_words(rows, column),
            "phrases": [
                {"label": label, "value": phrase_count(rows, column, label)}
                for label in PHRASE_LABELS[key]
                if phrase_count(rows, column, label) > 0
            ],
            "totalResponses": len(answers),
        }

    output = BASE_DIR / "data.json"
    output.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("{} gerado a partir de {} ({} respostas).".format(output.name, csv_path.name, len(rows)))


if __name__ == "__main__":
    main()
