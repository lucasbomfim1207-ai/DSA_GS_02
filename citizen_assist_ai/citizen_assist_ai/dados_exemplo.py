"""Registros de exemplo (fictícios/ilustrativos) para demonstração do sistema."""

EXEMPLOS = [
    (101, "Vacinação de rotina", "Saúde",
     "Aplicação das vacinas do calendário de imunização nas unidades básicas de saúde.",
     "Documento com foto e caderneta de vacinação", "UBS do bairro"),
    (102, "Consulta médica na UBS", "Saúde",
     "Atendimento de clínica geral, pré-natal e acompanhamento de doenças crônicas.",
     "Documento com foto, CPF e comprovante de residência", "UBS do bairro"),
    (201, "Cadastro Único (CadÚnico)", "Assistência Social",
     "Registro de famílias de baixa renda para acesso a programas sociais.",
     "Documento de todos os moradores e comprovante de residência", "CRAS do território"),
    (202, "Benefício de Prestação Continuada", "Assistência Social",
     "Apoio financeiro a idosos e pessoas com deficiência que atendam aos critérios de renda.",
     "CadÚnico atualizado, CPF e documentos do requerente", "CRAS ou agência do INSS"),
    (301, "Emissão de carteira de identidade", "Documentação",
     "Primeira e segunda via da carteira de identidade nacional.",
     "Certidão de nascimento ou casamento, CPF e comprovante de residência", "Posto de identificação civil"),
    (302, "Título de eleitor", "Documentação",
     "Emissão, transferência de domicílio e regularização do título de eleitor.",
     "Documento com foto, comprovante de residência e quitação militar (se aplicável)", "Cartório eleitoral"),
    (401, "Qualificação profissional gratuita", "Educação",
     "Cursos curtos de qualificação para ingresso no mercado de trabalho.",
     "Idade mínima de 16 anos, documento com foto e comprovante de residência", "Centro de formação profissional"),
    (402, "Educação de Jovens e Adultos (EJA)", "Educação",
     "Ensino fundamental e médio para quem não concluiu os estudos na idade regular.",
     "Documento com foto e histórico escolar (se houver)", "Escolas da rede pública"),
    (501, "Reparo de iluminação pública", "Serviços Urbanos",
     "Solicitação de conserto de lâmpadas e postes queimados ou danificados.",
     "Endereço exato e ponto de referência do poste", "Central de atendimento 156 ou aplicativo"),
    (502, "Poda de árvore em via pública", "Serviços Urbanos",
     "Pedido de avaliação e poda de árvores que ofereçam risco ou bloqueiem a via.",
     "Endereço exato e foto da árvore (opcional)", "Central de atendimento 156 ou subprefeitura"),
]


def carregar_exemplos(gerenciador):
    for registro in EXEMPLOS:
        gerenciador.cadastrar(*registro)
