# Backlog priorizado — ClassSync

> Este arquivo é o espelho versionado do backlog que deve ser replicado no GitHub Projects.

| ID | Prioridade | Título | Descrição | Critérios de aceitação | Sprint | Responsável | Estado |
|---|---:|---|---|---|---|---|---|
| US-01 | 1 | Calendário público | Permitir que estudantes consultem compromissos da turma sem editar dados. | Dado um visitante, quando acessar a home, então o calendário e os eventos são exibidos sem login. | S1 | Integrante A | Concluído |
| US-02 | 2 | Modelo relacional | Criar turma, usuários e eventos relacionados em SQLite. | Ao iniciar uma instalação limpa, as três tabelas são criadas e os dados permanecem após reinício. | S1 | Integrante A | Concluído |
| US-03 | 3 | Cadastro de estudante | Permitir que um aluno crie sua conta com e-mail e senha válidos. | Com dados válidos, o cadastro é salvo com senha em hash; e-mail duplicado ou senha curta é rejeitado. | S2 | Integrante B | Concluído |
| US-04 | 4 | Login e logout | Autenticar estudantes e líderes e encerrar sessão. | Credenciais válidas criam sessão; credenciais inválidas não entram; logout remove acesso. | S2 | Integrante B | Concluído |
| US-05 | 5 | Autorização por papel | Restringir CRUD de eventos a líder/admin. | Estudante pode consultar, mas recebe redirecionamento ao tentar acessar `/admin`. | S2 | Integrante C | Concluído |
| US-06 | 6 | CRUD de eventos | Criar, listar, editar e excluir compromissos. | Líder salva evento válido, vê na listagem, altera dados e exclui com confirmação. | S2 | Integrante A | Concluído |
| US-07 | 7 | Validação e erros | Tratar dados inválidos e registros inexistentes. | Datas, título e categoria inválidos retornam mensagem; registro inexistente retorna 404 amigável. | S2 | Integrante C | Concluído |
| US-08 | 8 | Testes de sistema | Automatizar os fluxos principais. | Suíte possui pelo menos 16 testes e todos passam com `pytest -q`. | S3 | Integrante B | Concluído |
| US-09 | 9 | Implantação | Disponibilizar configuração de produção. | `gunicorn` inicia a aplicação com `PORT` e `DATABASE_URL` configuráveis. | S3 | Integrante A | Em Teste |
| US-10 | 10 | Documentação e apresentação | Consolidar README, limitações e evidências. | README permite instalação limpa e apresentação explica problema, banco, autenticação e testes. | S3 | Integrante C | Em Andamento |

## Regra de validação

Toda tarefa só pode ser movida para **Concluído** após um integrante diferente do responsável registrar a execução do critério de aceitação no histórico do GitHub Projects.
