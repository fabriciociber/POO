# ClassSync — calendário acadêmico

Aplicação web Flask para centralizar provas, trabalhos, apresentações e eventos de uma turma. Estudantes podem consultar o calendário e criar suas contas; líderes podem gerenciar os compromissos.

## Funcionalidades

A aplicação possui calendário público, cadastro de estudantes, login, logout, hash seguro de senhas, autorização por papel, CRUD de compromissos, validações server-side, mensagens de retorno, tratamento de 404/500 e API JSON para o FullCalendar.

## Tecnologias

Flask 3.1, Flask-SQLAlchemy, SQLite, Bootstrap 5, FullCalendar 6, pytest e Gunicorn. Os modelos estão separados em `models.py`; as rotas e regras de aplicação estão em `app.py`; os templates estão em `templates/`.

## Instalação limpa

```bash
git clone URL_DO_REPOSITORIO
cd classsync
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY="uma-chave-secreta-forte"
python app.py
```

Acesse `http://localhost:5000`. Na primeira inicialização, o SQLite é criado em `instance/classsync.db` com a turma e usuários demonstrativos. Os dados são persistidos no banco, não em variáveis de memória.

Para produção, use:

```bash
gunicorn --bind 0.0.0.0:${PORT:-5000} app:app
```

`DATABASE_URL` pode ser usado para apontar para outro banco relacional compatível. Em produção, configure `SECRET_KEY` e não utilize a chave padrão de desenvolvimento.

## Usuários de demonstração

| Perfil | E-mail | Senha | Permissões |
|---|---|---|---|
| Líder | `lider@classsync.local` | `demo-password` | Consulta e criação, edição e exclusão de eventos |
| Estudante | `aluno@classsync.local` | `demo-password` | Consulta do calendário |

As senhas são armazenadas com hash seguro usando Werkzeug. Nenhuma senha é salva em texto puro.

## Testes

A suíte contém 20 testes de sistema, cobrindo páginas, API, cadastro, hash, login, logout, autorização, validações, persistência e CRUD.

```bash
. .venv/bin/activate
pytest -q
```

## Banco e entidades

O banco possui as entidades `Class`, `User` e `AcademicEvent`. Uma turma possui vários usuários e eventos; cada evento pertence a uma turma e registra o usuário que o criou. A criação automática via `db.create_all()` permite executar a instalação sem configuração manual de tabelas.

## Processo ágil e evidências

Os artefatos versionados estão em `docs_backlog.md`, `docs_sprints.md` e `docs_kanban_participacao.md`. Eles devem ser replicados e mantidos no GitHub Projects, com exatamente as colunas `A Fazer`, `Em Andamento`, `Em Teste` e `Concluído`. O grupo deve substituir os campos de preenchimento por nomes e links reais, registrar as sprints de 15 dias, responsáveis, revisores, evidências, histórico e participação individual.

O backlog contém título, descrição e critérios de aceitação para cada tarefa. O teste de uma tarefa deve ser executado por integrante diferente do responsável e indicado no card correspondente.

## Implantação

O arquivo `Procfile` configura o Gunicorn para plataformas como Render, Railway ou Fly.io. A publicação permanente ainda exige que o grupo crie o serviço, configure as variáveis `SECRET_KEY`, `DATABASE_URL` e `PORT`, e registre a URL final neste README e no GitHub Projects.

## Limitações conhecidas

O protótipo trabalha com uma turma inicial e ainda não possui recuperação de senha, confirmação de e-mail ou integração de notificações. Essas limitações não impedem o fluxo central exigido: cadastro, autenticação, consulta e administração dos compromissos.
