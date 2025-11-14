No VS Code, abra o terminal integrado. Vá em View > Terminal (ou Exibir > Terminal).

No terminal (verifique se você está na pasta projeto_backend_python), digite o comando para criar a bolha. Vamos chamá-la de venv:

python -m venv venv

Uma nova pasta venv aparecerá. Agora, você precisa "ativar" essa bolha.

.\venv\Scripts\activate

Você saberá que funcionou porque o nome (venv) aparecerá antes do seu prompt no terminal.

Agora que sua "bolha" está ativa, instale tudo o que o api.py precisa. No mesmo terminal, rode:

pip install flask flask-cors ultralytics pandas openpyxl

Pronto! No mesmo terminal (com o (venv) ativo), rode o seu servidor:

python api.py

Você verá uma mensagem dizendo algo como Running on http://127.0.0.1:5000. Deixe este terminal rodando. Seu backend está pronto e esperando o frontend chamar.
