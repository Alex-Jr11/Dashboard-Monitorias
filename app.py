from pathlib import Path
import re
import unicodedata
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard de Monitorias",
    page_icon="📊",
    layout="wide"
)

PASTA_DADOS = "dadosAtualizados"
PADRAO_READ_AI = r"https://app\.read\.ai/analytics/meetings/[^\s,\"']+"

MAPA_MESES_PT = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
}

OPCOES_PERIODO_RAPIDO = [
    "Personalizado",
    "Hoje",
    "Ontem",
    "Últimos 7 dias",
    "Últimos 30 dias",
    "Mês atual",
    "Mês anterior",
]


# =========================
# ESTILO
# =========================
st.markdown("""
<style>
    .stApp {
        background-color: #0b0b12;
        color: white;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #171723 0%, #11111a 100%);
        border-right: 1px solid rgba(168, 85, 247, 0.18);
    }

    h1, h2, h3 {
        color: white;
    }

    div[data-testid="metric-container"] {
        background: #12121b;
        border: 1px solid rgba(168, 85, 247, 0.20);
        border-left: 4px solid #a855f7;
        padding: 16px;
        border-radius: 14px;
        box-shadow: 0 0 0 1px rgba(168, 85, 247, 0.05);
    }

    div[data-testid="metric-container"] label {
        color: #cfcfe6 !important;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: white;
    }

    hr {
        border-color: rgba(168, 85, 247, 0.15);
    }

    .filtro-box {
        background: linear-gradient(180deg, rgba(168,85,247,0.10) 0%, rgba(168,85,247,0.04) 100%);
        border: 1px solid rgba(168,85,247,0.18);
        border-radius: 14px;
        padding: 12px 14px;
        margin: 8px 0 16px 0;
    }

    .filtro-titulo {
        font-size: 15px;
        font-weight: 700;
        color: white;
        margin-bottom: 6px;
    }

    .filtro-texto {
        font-size: 12px;
        color: #d4d4e8;
        line-height: 1.4;
    }

    .stTextInput > div > div > input,
    .stDateInput input,
    .stNumberInput input {
        border: 1px solid rgba(168, 85, 247, 0.35) !important;
        background-color: #11111a !important;
        color: white !important;
    }

    .stTextInput > div > div > input:focus,
    .stDateInput input:focus,
    .stNumberInput input:focus {
        border: 1px solid #a855f7 !important;
        box-shadow: 0 0 0 1px #a855f7 !important;
    }

    div[data-baseweb="select"] > div {
        border: 1px solid rgba(168, 85, 247, 0.35) !important;
        border-radius: 10px !important;
        background-color: #11111a !important;
    }

    div[data-baseweb="select"] span {
        color: white !important;
    }

    .stSlider [data-baseweb="slider"] div[role="slider"] {
        background-color: #a855f7 !important;
        border-color: #a855f7 !important;
    }

    .stSlider [data-baseweb="slider"] div[data-testid="stTickBar"] {
        background: linear-gradient(90deg, rgba(168,85,247,0.35), rgba(168,85,247,0.75)) !important;
    }

    .stCheckbox label {
        color: #e5dbff !important;
    }

    input[type="checkbox"] {
        accent-color: #a855f7 !important;
    }

    details {
        background: linear-gradient(180deg, rgba(168,85,247,0.08) 0%, rgba(168,85,247,0.03) 100%);
        border: 1px solid rgba(168,85,247,0.18);
        border-radius: 12px;
        padding: 8px 10px;
    }

    details summary {
        color: white !important;
        font-weight: 600;
    }

    .stButton button {
        background: linear-gradient(180deg, #2b143e 0%, #241232 100%) !important;
        color: white !important;
        border: 1px solid rgba(168, 85, 247, 0.35) !important;
        border-radius: 10px !important;
    }

    .stButton button:hover {
        border: 1px solid #a855f7 !important;
        box-shadow: 0 0 0 1px rgba(168, 85, 247, 0.20) !important;
    }

    .stDownloadButton button {
        background: linear-gradient(180deg, #6b21a8 0%, #581c87 100%) !important;
        color: white !important;
        border: 1px solid rgba(147, 51, 234, 0.45) !important;
        border-radius: 10px !important;
    }

    .stDownloadButton button:hover {
        background: linear-gradient(180deg, #581c87 0%, #4c1d95 100%) !important;
        border: 1px solid #a855f7 !important;
        box-shadow: 0 0 0 1px rgba(168, 85, 247, 0.20) !important;
    }

    /* Filtro custom de matrícula */
    .matricula-bolinha {
        width: 12px;
        height: 12px;
        min-width: 12px;
        border-radius: 50%;
        border: 1px solid rgba(168, 85, 247, 0.45);
        background: transparent;
        display: inline-block;
        margin-top: 6px;
    }

    .matricula-bolinha.ativa {
        background: #a855f7;
        border-color: #a855f7;
    }
</style>
""", unsafe_allow_html=True)


# =========================
# ESTADO INICIAL DOS FILTROS
# =========================
def inicializar_estado_filtros():
    defaults = {
        "selecionar_todos_agentes": True,
        "busca_monitorias": "",
        "cidade_selecionada": "Todas",
        "modo_matricula": "Todas",
        "periodo_rapido": "Personalizado",
        "mes_especifico": "Todos",
        "data_inicio": None,
        "data_fim": None,
        "numero_min_personalizado": None,
        "numero_max_personalizado": None,
    }

    for chave, valor in defaults.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


def limpar_filtros():
    chaves_para_remover = [
        "selecionar_todos_agentes",
        "busca_monitorias",
        "cidade_selecionada",
        "modo_matricula",
        "periodo_rapido",
        "mes_especifico",
        "data_inicio",
        "data_fim",
        "numero_min_personalizado",
        "numero_max_personalizado",
    ]

    for chave in list(st.session_state.keys()):
        if chave in chaves_para_remover or chave.startswith("agente_") or chave.startswith("matricula_opt_"):
            del st.session_state[chave]

    inicializar_estado_filtros()


inicializar_estado_filtros()


# =========================
# FUNÇÕES AUXILIARES
# =========================
def limpar_texto(valor):
    if pd.isna(valor):
        return pd.NA
    valor = str(valor).strip()
    return valor if valor != "" else pd.NA


def normalizar_colunas(df):
    df.columns = [
        str(col)
        .replace("\ufeff", "")
        .replace("\xa0", " ")
        .strip()
        for col in df.columns
    ]
    return df


def tentar_ler_csv(caminho, **kwargs):
    tentativas = [
        {"encoding": "utf-8"},
        {"encoding": "utf-8-sig"},
        {"encoding": "latin1"},
        {"encoding": "cp1252"},
    ]

    ultimo_erro = None

    for tentativa in tentativas:
        try:
            df = pd.read_csv(
                caminho,
                on_bad_lines="skip",
                low_memory=False,
                **tentativa,
                **kwargs
            )
            return normalizar_colunas(df)
        except Exception as erro:
            ultimo_erro = erro

    if ultimo_erro:
        raise ultimo_erro

    raise ValueError(f"Não foi possível ler o arquivo: {caminho}")


def converter_data_robusta(serie):
    texto = serie.astype("string").str.strip()

    data_iso = pd.to_datetime(texto, format="%Y-%m-%d", errors="coerce")

    faltantes = data_iso.isna()
    if faltantes.any():
        data_br = pd.to_datetime(texto[faltantes], format="%d/%m/%Y", errors="coerce")
        data_iso.loc[faltantes] = data_br

    faltantes = data_iso.isna()
    if faltantes.any():
        data_flex = pd.to_datetime(texto[faltantes], errors="coerce", dayfirst=True)
        data_iso.loc[faltantes] = data_flex

    data_min_aceitavel = pd.Timestamp("2024-01-01")
    data_max_aceitavel = pd.Timestamp("2035-12-31")

    data_iso = data_iso.where(
        data_iso.isna() | (
            (data_iso >= data_min_aceitavel) &
            (data_iso <= data_max_aceitavel)
        ),
        pd.NaT
    )

    return data_iso


def extrair_url_read_ai(valor):
    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip()
    match = re.search(PADRAO_READ_AI, texto)

    if match:
        return match.group(0)

    return pd.NA


def extrair_cidade(matricula):
    if pd.isna(matricula):
        return "Não informado"

    m = str(matricula).upper().strip()

    if m.startswith("PDITA"):
        return "Itabira"
    if m.startswith("PDBD"):
        return "Bom Despacho"

    return "Outro"


def extrair_numero_matricula(matricula):
    if pd.isna(matricula):
        return pd.NA

    numeros = re.findall(r"\d+", str(matricula))
    if numeros:
        return int(numeros[-1])

    return pd.NA


def normalizar_agente_sucesso(valor):
    if pd.isna(valor):
        return "Não informado"

    texto = str(valor).strip()
    texto_normalizado = re.sub(r"\s+", " ", texto).lower()

    mapa_agentes = {
        "ryan": "Ryan Lage",
        "ryan lage": "Ryan Lage",
        "ryan lague": "Ryan Lage"
    }

    return mapa_agentes.get(texto_normalizado, texto)


def slug_texto(texto):
    return re.sub(r"[^a-zA-Z0-9_]", "_", str(texto).strip().lower())


def normalizar_nome_para_chave(nome):
    if pd.isna(nome):
        return pd.NA

    texto = str(nome).strip().upper()
    texto = re.sub(r"\s+", " ", texto)
    return texto if texto else pd.NA


def remover_acentos(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto)
    return "".join(
        c for c in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(c)
    )


def normalizar_texto_busca(texto):
    texto = remover_acentos(texto).lower().strip()
    texto = re.sub(r"\s+", " ", texto)
    return texto


def matricula_valida(valor):
    if pd.isna(valor):
        return False

    texto = str(valor).strip().upper()

    if texto in {"", "0", "N/D", "NA", "NÃO INFORMADO", "NAO INFORMADO"}:
        return False

    return bool(re.fullmatch(r"(PDITA|PDBD)\d+", texto))


def normalizar_status_monitoria(valor):
    if pd.isna(valor):
        return "Presente"

    texto = str(valor).strip()
    texto_normalizado = re.sub(r"\s+", " ", texto).lower()

    mapa_status = {
        "presente": "Presente",
        "presença": "Presente",
        "presenca": "Presente",
        "compareceu": "Presente",
        "faltou": "Faltou",
        "ausente": "Faltou",
        "falta": "Faltou",
        "não informado": "Presente",
        "nao informado": "Presente",
        "": "Presente"
    }

    return mapa_status.get(texto_normalizado, texto)


def montar_opcoes_mes(df):
    datas_validas = df["data"].dropna()
    if datas_validas.empty:
        return ["Todos"]

    periodos = sorted(datas_validas.dt.to_period("M").unique(), reverse=True)
    opcoes = ["Todos"]

    for periodo in periodos:
        mes = MAPA_MESES_PT.get(periodo.month, str(periodo.month))
        opcoes.append(f"{mes}/{periodo.year}")

    return opcoes


def aplicar_filtro_mes(df, mes_especifico):
    if mes_especifico == "Todos":
        return df

    try:
        nome_mes, ano = mes_especifico.split("/")
        ano = int(ano)

        numero_mes = None
        for chave, valor in MAPA_MESES_PT.items():
            if valor == nome_mes:
                numero_mes = chave
                break

        if numero_mes is None:
            return df

        return df[
            (df["data"].dt.month == numero_mes) &
            (df["data"].dt.year == ano)
        ]
    except Exception:
        return df


def obter_intervalo_periodo_rapido(opcao, data_min, data_max):
    hoje = pd.Timestamp.today().normalize()

    if opcao == "Hoje":
        return hoje.date(), hoje.date()

    if opcao == "Ontem":
        ontem = hoje - pd.Timedelta(days=1)
        return ontem.date(), ontem.date()

    if opcao == "Últimos 7 dias":
        inicio = hoje - pd.Timedelta(days=6)
        return max(inicio.date(), data_min), min(hoje.date(), data_max)

    if opcao == "Últimos 30 dias":
        inicio = hoje - pd.Timedelta(days=29)
        return max(inicio.date(), data_min), min(hoje.date(), data_max)

    if opcao == "Mês atual":
        inicio = hoje.replace(day=1)
        return max(inicio.date(), data_min), min(hoje.date(), data_max)

    if opcao == "Mês anterior":
        inicio_mes_atual = hoje.replace(day=1)
        fim_mes_anterior = inicio_mes_atual - pd.Timedelta(days=1)
        inicio_mes_anterior = fim_mes_anterior.replace(day=1)
        return max(inicio_mes_anterior.date(), data_min), min(fim_mes_anterior.date(), data_max)

    return data_min, data_max


def aplicar_busca_inteligente(df, termo_busca):
    termo_busca = normalizar_texto_busca(termo_busca)
    if not termo_busca:
        return df

    termos = [t for t in termo_busca.split(" ") if t]
    if not termos:
        return df

    base_busca = (
        df["nome"].fillna("").astype(str) + " " +
        df["matricula"].fillna("").astype(str) + " " +
        df["agente_sucesso"].fillna("").astype(str)
    ).apply(normalizar_texto_busca)

    mascara = pd.Series(True, index=df.index)

    for termo in termos:
        mascara &= base_busca.str.contains(re.escape(termo), na=False)

    return df[mascara]


def padronizar_dataframe(df, arquivo_origem):
    colunas_finais = [
        "nome",
        "matricula",
        "data",
        "agente_sucesso",
        "status_monitoria",
        "link_monitoria",
        "resumo",
        "comentarios",
        "justificativa",
        "arquivo_origem"
    ]

    for col in colunas_finais:
        if col not in df.columns:
            df[col] = pd.NA

    df = df[colunas_finais].copy()
    df["arquivo_origem"] = arquivo_origem

    for col in [
        "nome",
        "matricula",
        "agente_sucesso",
        "status_monitoria",
        "link_monitoria",
        "resumo",
        "comentarios",
        "justificativa"
    ]:
        df[col] = df[col].apply(limpar_texto)

    df["link_monitoria"] = df["link_monitoria"].apply(extrair_url_read_ai)
    df["data"] = converter_data_robusta(df["data"])

    df["nome"] = df["nome"].fillna("Não informado")
    df["matricula"] = df["matricula"].fillna(pd.NA)
    df["agente_sucesso"] = df["agente_sucesso"].apply(normalizar_agente_sucesso)
    df["status_monitoria"] = df["status_monitoria"].apply(normalizar_status_monitoria)
    df["resumo"] = df["resumo"].fillna("")

    df["cidade"] = df["matricula"].apply(extrair_cidade)
    df["numero_matricula"] = df["matricula"].apply(extrair_numero_matricula)

    return df


def corrigir_matriculas_por_historico(df):
    df = df.copy()

    df["nome_chave"] = df["nome"].apply(normalizar_nome_para_chave)

    base_matriculas_validas = df[
        df["nome_chave"].notna() &
        df["matricula"].apply(matricula_valida)
    ].copy()

    if not base_matriculas_validas.empty:
        base_matriculas_validas["matricula"] = (
            base_matriculas_validas["matricula"].astype(str).str.strip().str.upper()
        )

        referencia = (
            base_matriculas_validas
            .groupby(["nome_chave", "matricula"])
            .size()
            .reset_index(name="qtd")
            .sort_values(["nome_chave", "qtd", "matricula"], ascending=[True, False, True])
            .drop_duplicates(subset=["nome_chave"], keep="first")
            .rename(columns={"matricula": "matricula_referencia"})
        )

        df = df.merge(
            referencia[["nome_chave", "matricula_referencia"]],
            on="nome_chave",
            how="left"
        )

        precisa_corrigir = ~df["matricula"].apply(matricula_valida)

        df.loc[precisa_corrigir & df["matricula_referencia"].notna(), "matricula"] = (
            df.loc[precisa_corrigir & df["matricula_referencia"].notna(), "matricula_referencia"]
        )

        df = df.drop(columns=["matricula_referencia"], errors="ignore")

    df["cidade"] = df["matricula"].apply(extrair_cidade)
    df["numero_matricula"] = df["matricula"].apply(extrair_numero_matricula)

    return df


def selecionar_modo_matricula_sidebar():
    opcoes = ["Todas", "Até 500", "Acima de 500", "Faixa personalizada"]

    for opcao in opcoes:
        col1, col2 = st.sidebar.columns([1, 18], gap="small")
        ativa = st.session_state["modo_matricula"] == opcao

        with col1:
            classe = "matricula-bolinha ativa" if ativa else "matricula-bolinha"
            st.markdown(f'<div class="{classe}"></div>', unsafe_allow_html=True)

        with col2:
            if st.button(opcao, key=f"matricula_opt_{opcao}", use_container_width=False):
                st.session_state["modo_matricula"] = opcao
                st.rerun()


# =========================
# LEITURA DOS CSVs
# =========================
def ler_relatorios_monitoria(caminho):
    df = tentar_ler_csv(caminho)

    df = df.rename(columns={
        "Nome do aluno": "nome",
        "Matrícula": "matricula",
        "Data": "data",
        "Agente de Sucesso": "agente_sucesso",
        "Status da Monitoria": "status_monitoria",
        "Relatório do Read IA": "resumo",
        "Link do Read IA": "link_monitoria",
        "Motivo da Falta": "justificativa",
        "Outro Motivo:": "comentarios"
    })

    return padronizar_dataframe(df, Path(caminho).name)


def ler_acompanhamento(caminho):
    df = tentar_ler_csv(caminho, skiprows=2)

    df = df.rename(columns={
        "Nome do Aluno:": "nome",
        "Matrícula:": "matricula",
        "Data:": "data",
        "Agente de Sucesso:": "agente_sucesso",
        "Status Monitoria:": "status_monitoria",
        "Resumo Read .IA:": "resumo",
        "Link Gravação Read .IA:": "link_monitoria",
        "Justificativa:": "justificativa",
        "Comentários sobre a Monitoria:": "comentarios"
    })

    return padronizar_dataframe(df, Path(caminho).name)


def ler_agentes_sucesso(caminho):
    df = tentar_ler_csv(caminho, skiprows=4)

    df = df.rename(columns={
        "Nome": "nome",
        "Matrícula :": "matricula",
        "Data": "data",
        "Agente de Sucesso": "agente_sucesso",
        "Status Monitoria": "status_monitoria",
        "Resumo": "resumo",
        "Resumo Read.IA": "resumo",
        "Link Gravação Read.IA": "link_monitoria",
        "Justificativa": "justificativa",
        "Comentários sobre a Monitoria": "comentarios"
    })

    return padronizar_dataframe(df, Path(caminho).name)


def ler_monitorias_agentes(caminho):
    df = tentar_ler_csv(caminho, skiprows=4)

    df = df.rename(columns={
        "Nome": "nome",
        "Matrícula :": "matricula",
        "Data": "data",
        "Agente de Sucesso": "agente_sucesso",
        "Status": "status_monitoria",
        "Status Monitoria": "status_monitoria",
        "Resumo Read.IA": "resumo",
        "Link Gravação Read.IA": "link_monitoria",
        "Justificativa": "justificativa",
        "Comentários sobre a Monitoria": "comentarios"
    })

    return padronizar_dataframe(df, Path(caminho).name)


def ler_acao_intensivao(caminho):
    df = tentar_ler_csv(caminho, skiprows=2)

    df = df.rename(columns={
        "Nome do Aluno:": "nome",
        "Matricula:": "matricula",
        "Matrícula:": "matricula",
        "Data": "data",
        "Agente de Sucesso:": "agente_sucesso",
        "Status Monitoria:": "status_monitoria",
        "Resumo Read.IA:": "resumo",
        "Resumo Read .IA:": "resumo",
        "Link Gravação Read.IA:": "link_monitoria",
        "Link Gravação Read .IA:": "link_monitoria",
        "Justificativa:": "justificativa",
        "Comentários sobre a Monitoria:": "comentarios"
    })

    return padronizar_dataframe(df, Path(caminho).name)


def ler_arquivo(caminho):
    nome = Path(caminho).name.lower()

    if "relatórios monitoria" in nome or "relatorios monitoria" in nome:
        return ler_relatorios_monitoria(caminho)

    if "ação intensivão" in nome or "acao intensivao" in nome:
        return ler_acao_intensivao(caminho)

    if "monitorias agentes de sucesso" in nome:
        return ler_monitorias_agentes(caminho)

    if "agentes de sucesso" in nome:
        return ler_agentes_sucesso(caminho)

    if "acompanhamento" in nome:
        return ler_acompanhamento(caminho)

    return pd.DataFrame()


# =========================
# CONSOLIDAÇÃO
# =========================
@st.cache_data
def consolidar_bases(pasta_dados):
    pasta = Path(pasta_dados)

    if not pasta.exists():
        return pd.DataFrame()

    arquivos = sorted(pasta.glob("*.csv"))
    dfs = []

    for arquivo in arquivos:
        try:
            df = ler_arquivo(arquivo)
            if not df.empty:
                dfs.append(df)
        except Exception:
            continue

    if not dfs:
        return pd.DataFrame()

    bruto = pd.concat(dfs, ignore_index=True)

    validos = bruto.dropna(subset=["link_monitoria"]).copy()

    validos["status_monitoria"] = validos["status_monitoria"].apply(normalizar_status_monitoria)
    validos["status_monitoria"] = validos["status_monitoria"].replace(
        {"Não informado": "Presente"}
    ).fillna("Presente")

    validos = corrigir_matriculas_por_historico(validos)

    validos["matricula"] = validos["matricula"].fillna("Não informado")
    validos["cidade"] = validos["cidade"].fillna("Não informado")

    validos["data"] = validos["data"].where(
        validos["data"].isna() | (
            (validos["data"] >= pd.Timestamp("2024-01-01")) &
            (validos["data"] <= pd.Timestamp("2035-12-31"))
        ),
        pd.NaT
    )

    final = validos.drop_duplicates(
        subset=["nome", "matricula", "data", "link_monitoria"],
        keep="first"
    ).copy()

    final["data_formatada"] = final["data"].dt.strftime("%d/%m/%Y")
    final["data_formatada"] = final["data_formatada"].fillna("Sem data")

    return final.sort_values(by="data", ascending=False, na_position="last")


# =========================
# FILTROS
# =========================
def aplicar_filtros(df):
    st.sidebar.header("Filtros")

    agentes = sorted([
        a for a in df["agente_sucesso"].dropna().astype(str).str.strip().unique().tolist()
        if a != "Não informado"
    ])

    st.sidebar.markdown("**Agente de sucesso**")

    selecionar_todos_agentes = st.sidebar.checkbox(
        "Selecionar todos os agentes",
        key="selecionar_todos_agentes"
    )

    agente_selecionado = []

    if not selecionar_todos_agentes:
        with st.sidebar.expander("Escolher agentes", expanded=False):
            for agente in agentes:
                marcado = st.checkbox(
                    agente,
                    value=st.session_state.get(f"agente_{slug_texto(agente)}", False),
                    key=f"agente_{slug_texto(agente)}"
                )
                if marcado:
                    agente_selecionado.append(agente)

    busca = st.sidebar.text_input(
        "Buscar por nome, matrícula ou agente",
        key="busca_monitorias",
        placeholder="Ex.: julia pdita, andre, joao"
    )

    cidades = [
        c for c in sorted(df["cidade"].dropna().astype(str).str.strip().unique().tolist())
        if c not in ["Não informado", "Outro"]
    ]

    cidade_opcoes = ["Todas"] + cidades

    st.sidebar.selectbox(
        "Cidade",
        options=cidade_opcoes,
        key="cidade_selecionada"
    )

    numeros_validos = pd.to_numeric(df["numero_matricula"], errors="coerce").dropna()

    if numeros_validos.empty:
        numero_min_padrao = 0
        numero_max_padrao = 1000
    else:
        numero_min_padrao = int(numeros_validos.min())
        numero_max_padrao = int(min(numeros_validos.max(), 1000))

    st.sidebar.markdown("""
    <div class="filtro-box">
        <div class="filtro-titulo">🎯 Faixa de matrículas</div>
        <div class="filtro-texto">
            Escolha rapidamente como deseja visualizar as matrículas da cidade selecionada.
        </div>
    </div>
    """, unsafe_allow_html=True)

    selecionar_modo_matricula_sidebar()

    numero_min = numero_min_padrao
    numero_max = numero_max_padrao

    modo_matricula = st.session_state["modo_matricula"]

    if modo_matricula == "Até 500":
        numero_min = numero_min_padrao
        numero_max = 500

    elif modo_matricula == "Acima de 500":
        numero_min = 501
        numero_max = numero_max_padrao

    elif modo_matricula == "Faixa personalizada":
        if st.session_state.get("numero_min_personalizado") is None:
            st.session_state["numero_min_personalizado"] = numero_min_padrao
        if st.session_state.get("numero_max_personalizado") is None:
            st.session_state["numero_max_personalizado"] = numero_max_padrao

        faixa = st.sidebar.slider(
            "Selecione a faixa numérica",
            min_value=numero_min_padrao,
            max_value=1000,
            value=(
                max(numero_min_padrao, st.session_state["numero_min_personalizado"]),
                min(1000, st.session_state["numero_max_personalizado"])
            )
        )
        numero_min, numero_max = faixa
        st.session_state["numero_min_personalizado"] = numero_min
        st.session_state["numero_max_personalizado"] = numero_max

    datas_validas = df["data"].dropna()
    datas_validas = datas_validas[
        (datas_validas >= pd.Timestamp("2024-01-01")) &
        (datas_validas <= pd.Timestamp("2035-12-31"))
    ]

    if datas_validas.empty:
        st.sidebar.warning("Nenhuma data válida encontrada nos arquivos.")
        return df

    data_min = datas_validas.min().date()
    data_max = datas_validas.max().date()

    st.sidebar.markdown("**Período dos dados**")
    st.sidebar.caption(f"De {data_min.strftime('%d/%m/%Y')} até {data_max.strftime('%d/%m/%Y')}")

    st.sidebar.selectbox(
        "Atalho de período",
        options=OPCOES_PERIODO_RAPIDO,
        key="periodo_rapido"
    )

    mes_opcoes = montar_opcoes_mes(df)
    if st.session_state.get("mes_especifico") not in mes_opcoes:
        st.session_state["mes_especifico"] = "Todos"

    st.sidebar.selectbox(
        "Mês específico",
        options=mes_opcoes,
        key="mes_especifico"
    )

    data_inicio_default, data_fim_default = obter_intervalo_periodo_rapido(
        st.session_state["periodo_rapido"],
        data_min,
        data_max
    )

    if st.session_state["periodo_rapido"] == "Personalizado":
        if st.session_state.get("data_inicio") is None:
            st.session_state["data_inicio"] = data_min
        if st.session_state.get("data_fim") is None:
            st.session_state["data_fim"] = data_max

        data_inicio = st.sidebar.date_input(
            "Data inicial",
            min_value=data_min,
            max_value=data_max,
            key="data_inicio",
            format="DD/MM/YYYY"
        )

        data_fim = st.sidebar.date_input(
            "Data final",
            min_value=data_min,
            max_value=data_max,
            key="data_fim",
            format="DD/MM/YYYY"
        )
    else:
        st.session_state["data_inicio"] = data_inicio_default
        st.session_state["data_fim"] = data_fim_default

        data_inicio = st.sidebar.date_input(
            "Data inicial",
            min_value=data_min,
            max_value=data_max,
            key="data_inicio",
            format="DD/MM/YYYY",
            disabled=True
        )

        data_fim = st.sidebar.date_input(
            "Data final",
            min_value=data_min,
            max_value=data_max,
            key="data_fim",
            format="DD/MM/YYYY",
            disabled=True
        )

    df_filtrado = df.copy()

    if not selecionar_todos_agentes and agente_selecionado:
        df_filtrado = df_filtrado[df_filtrado["agente_sucesso"].isin(agente_selecionado)]

    if busca:
        df_filtrado = aplicar_busca_inteligente(df_filtrado, busca)

    if st.session_state["cidade_selecionada"] != "Todas":
        df_filtrado = df_filtrado[df_filtrado["cidade"] == st.session_state["cidade_selecionada"]]

    df_filtrado = df_filtrado[
        (pd.to_numeric(df_filtrado["numero_matricula"], errors="coerce").fillna(0) >= numero_min) &
        (pd.to_numeric(df_filtrado["numero_matricula"], errors="coerce").fillna(0) <= numero_max)
    ]

    df_filtrado = aplicar_filtro_mes(df_filtrado, st.session_state["mes_especifico"])

    if data_inicio and data_fim:
        inicio = pd.Timestamp(min(data_inicio, data_fim))
        fim = pd.Timestamp(max(data_inicio, data_fim))
        df_filtrado = df_filtrado[df_filtrado["data"].between(inicio, fim)]

    st.sidebar.markdown("---")
    if st.sidebar.button("🧹 Limpar filtros", use_container_width=True):
        limpar_filtros()
        st.rerun()

    return df_filtrado


# =========================
# DASHBOARD
# =========================
st.title("📊 Dashboard de Monitorias")

if not Path(PASTA_DADOS).exists():
    st.error("A pasta 'dadosAtualizados' não foi encontrada.")
    st.stop()

df = consolidar_bases(PASTA_DADOS)

if df.empty:
    st.error("Nenhum CSV válido foi encontrado na pasta 'dadosAtualizados'.")
    st.stop()

df_filtrado = aplicar_filtros(df)

total_monitorias = len(df_filtrado)
st.metric("Total de monitorias", total_monitorias)

st.divider()
st.subheader("Monitorias consolidadas")

tabela = df_filtrado[
    [
        "data_formatada",
        "nome",
        "matricula",
        "cidade",
        "agente_sucesso",
        "status_monitoria",
        "link_monitoria"
    ]
].rename(columns={
    "data_formatada": "Data",
    "nome": "Nome",
    "matricula": "Matrícula",
    "cidade": "Cidade",
    "agente_sucesso": "Agente de sucesso",
    "status_monitoria": "Status da monitoria",
    "link_monitoria": "Link da monitoria"
})

st.dataframe(
    tabela,
    width="stretch",
    hide_index=True,
    column_config={
        "Link da monitoria": st.column_config.LinkColumn(
            "Link da monitoria",
            display_text="Abrir link"
        )
    }
)

csv_export = (
    df_filtrado.drop(columns=["data_formatada", "arquivo_origem", "nome_chave"], errors="ignore")
    .to_csv(index=False, encoding="utf-8-sig")
    .encode("utf-8-sig")
)

st.download_button(
    label="📥 Baixar CSV filtrado",
    data=csv_export,
    file_name="monitorias_filtradas.csv",
    mime="text/csv",
    width="stretch"
)