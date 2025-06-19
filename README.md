# Tray

Exemplo simples de API usando FastAPI para realizar upload de arquivos para um bucket S3.

## Configuração

Antes de executar a aplicação defina as variáveis de ambiente com suas credenciais AWS e o bucket alvo:

```
export AWS_ACCESS_KEY_ID=<seu_access_key>
export AWS_SECRET_ACCESS_KEY=<seu_secret_key>
export AWS_REGION=<regiao>
export BUCKET_NAME=qrcode-test-jd  # opcional, este é o valor padrão
```

Instale as dependências em um ambiente virtual e execute o servidor:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Também é possível executar a aplicação em um contêiner Docker:

```
docker build -t tray-api .
docker run -p 8000:8000 \
  -e AWS_ACCESS_KEY_ID=<seu_access_key> \
  -e AWS_SECRET_ACCESS_KEY=<seu_secret_key> \
  -e AWS_REGION=<regiao> \
  -e BUCKET_NAME=qrcode-test-jd tray-api
```

## Uso

Envie um POST para `/upload/<nomeArquivo>` contendo o payload JWS no corpo da requisição.
O cabeçalho `Content-Type` deve ser obrigatoriamente `application/jose`.
O nome do arquivo será o fragmento final da URL e não deve conter extensão.
O payload será salvo na raiz do bucket S3 configurado.
Também é possível enviar o código PIX completo usando o endpoint `/upload_by_qr`,
que recebe o parâmetro `qr_string` contendo o QR Code e utiliza o campo 25 para
definir o caminho do objeto no S3.
