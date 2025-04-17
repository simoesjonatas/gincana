# 📝 Manual do Sistema de Rankeamento – Gincana Kids PIBVP

Este projeto foi desenvolvido para facilitar o acompanhamento semanal das atividades da Gincana do Departamento Kids da PIBVP. O sistema permite cadastrar crianças, atividades, semanas e resultados, calculando automaticamente a pontuação total e gerando um ranking visual acessível publicamente.

---

## 🚀 Funcionalidades

- Cadastro de crianças por nome e turma
- Definição de semanas de gincana
- Registro de atividades com valor de pontuação
- Lançamento de resultados por criança, semana e atividade
- Cálculo automático da pontuação total
- Visualização do ranking com medalhas para os 3 primeiros lugares
- Inclusão de crianças mesmo sem pontuação (pontuação zerada)
- Interface administrativa com filtros e busca
- Página pública de ranking responsiva

---

## ⚙️ Tecnologias Utilizadas

- Python 3.x
- Django 5.x
- HTML5 + CSS3 (template customizado)
- SQLite (ou PostgreSQL)
- Admin do Django aprimorado
- ReportLab (para geração de PDF)

---

## 📦 Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seuusuario/gincana-kids-pibvp.git
   cd gincana-kids-pibvp
   ```

2. Crie um ambiente virtual e ative:
   ```bash
   python -m venv venv
   source venv/bin/activate  # ou venv\Scripts\activate no Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Realize as migrações:
   ```bash
   python manage.py migrate
   ```

5. Crie um superusuário para acessar o admin:
   ```bash
   python manage.py createsuperuser
   ```

6. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```

Acesse em: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)  
Ranking público: [http://127.0.0.1:8000/ranking/](http://127.0.0.1:8000/ranking/)

---

## 📄 Documentação

O manual completo do sistema está disponível em PDF:

- [Manual Simples – Uso geral](./docs/manual_gincana_kids_pibvp_custom.pdf)
<!-- - [Manual Simples – Uso geral](./docs/manual_gincana_kids_pibvp.pdf) -->
- [Manual Profissional – Apresentação institucional](./docs/manual_gincana_kids_pibvp_pro.pdf)

---

## 🙌 Contribuição

Contribuições são bem-vindas! Você pode ajudar:

- Criando novos filtros e relatórios no admin
- Melhorando o layout do ranking público
- Exportando ranking para PDF/Excel
- Adaptando para uso em outras igrejas

---

## 📬 Contato

Para dúvidas ou sugestões, entre em contato com a coordenação do Departamento Kids ou com a equipe técnica deste repositório.

---

**Feito com 💛 para servir melhor**
