# Dashboard de pesquisa: percepções sobre IA na formação docente

## Arquivos
- `index.html`: interface e gráficos (HTML, CSS, JavaScript e Chart.js).
- `data.json`: contagens agregadas calculadas a partir do CSV original. Não contém timestamps nem respostas abertas individuais.

## Executar localmente
O navegador pode bloquear `fetch()` quando o arquivo é aberto diretamente por `file://`. Na pasta do projeto, execute:

```bash
python3 -m http.server 8000
```

Depois abra `http://localhost:8000`.

## Publicar gratuitamente no GitHub Pages
1. Crie um repositório público no GitHub (por exemplo, `dashboard-pesquisa-ia`).
2. Envie `index.html`, `data.json` e este README. **Não envie o CSV original** se ele contiver dados pessoais ou respostas abertas.
3. No repositório, abra **Settings → Pages**.
4. Em **Build and deployment**, selecione **Deploy from a branch**.
5. Selecione a branch `main` e a pasta `/ (root)`, depois salve.
6. Aguarde a publicação. O GitHub mostrará o endereço público do site na seção Pages.

## Atualizar os gráficos
Se novas respostas forem coletadas, gere novamente as contagens agregadas e substitua `data.json`. O site não precisa de servidor próprio.

## Cuidados acadêmicos e de privacidade
- Este protótipo publica somente contagens agregadas; respostas abertas e timestamps não são publicados.
- Confirme a autorização/consentimento para divulgação dos resultados e evite publicar grupos com contagens muito pequenas quando isso puder identificar participantes.
- O dashboard é descritivo: não generalize resultados de uma amostra pequena para toda a população.
- Verifique a precisão e a fonte das afirmações sobre normas/diretrizes mencionadas no instrumento antes de apresentá-las como fatos no TCC.


## Nuvens de palavras
O dashboard também inclui nuvens de palavras para as duas perguntas abertas. As nuvens usam frequências calculadas localmente a partir das respostas, com palavras comuns removidas. O `data.json` contém apenas contagens agregadas, não os textos originais. Expressões recorrentes são mostradas separadamente.
