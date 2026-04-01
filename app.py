from pathlib import Path
import re
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard de Monitorias",
    page_icon="📊",
    layout="wide"
)

PASTA_DADOS = "dadosAtualizados"
PADRAO_READ_AI = r"https://app\.read\.ai/analytics/meetings/[^\s,\"']+"


# =========================
# AJUSTES VISUAIS EXTRAS
# =========================
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)


def limpar_texto(valor):
    if pd.isna(valor):
        return pd.NA
    valor = str(valor).strip()
    return valor if valor != "" else pd.NA


def converter_data_robusta(serie):
    texto = serie.astype("string").str.strip()

    data_iso = pd.to_datetime(texto, format="%Y-%m-%d", errors="coerce")

    faltantes = data_iso.isna()
    if faltantes.any():
        data_br = pd.to_datetime(texto[faltantes], format="%d/%m/%Y", errors="coerce")
        data_iso.loc[faltantes] = data_br

    return data_iso


def extrair_url_read_ai(valor):
    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip()
    match = re.search(PADRAO_READ_AI, texto)

    if match:
        return match.group(0)

    return pd.NA


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
    df["matricula"] = df["matricula"].fillna("Não informado")
    df["agente_sucesso"] = df["agente_sucesso"].fillna("Não informado")
    df["status_monitoria"] = df["status_monitoria"].fillna("Não informado")
    df["resumo"] = df["resumo"].fillna("")

    return df


def ler_relatorios_monitoria(caminho):
    df = pd.read_csv(caminho, encoding="utf-8")

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
    df = pd.read_csv(caminho, skiprows=2, encoding="utf-8")

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
    df = pd.read_csv(caminho, skiprows=4, encoding="utf-8")

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
    df = pd.read_csv(caminho, skiprows=4, encoding="utf-8")

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
    df = pd.read_csv(caminho, skiprows=2, encoding="utf-8")

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

    final = validos.drop_duplicates(
        subset=["nome", "matricula", "data", "link_monitoria"],
        keep="first"
    ).copy()

    final["data_formatada"] = final["data"].dt.strftime("%d/%m/%Y")
    final["data_formatada"] = final["data_formatada"].fillna("Sem data")

    return final.sort_values(by="data", ascending=False, na_position="last")


def aplicar_filtros(df):
    st.sidebar.header("Filtros")

    agentes = sorted([
        a for a in df["agente_sucesso"].dropna().astype(str).str.strip().unique().tolist()
        if a != "Não informado"
    ])

    agente_selecionado = st.sidebar.multiselect(
        "Agente de sucesso",
        agentes,
        placeholder="Selecione o agente"
    )

    busca = st.sidebar.text_input("Buscar por nome ou matrícula")

    datas_validas = df["data"].dropna()

    if datas_validas.empty:
        return df

    data_min = datas_validas.min().date()
    data_max = datas_validas.max().date()

    st.sidebar.markdown("**Período dos dados**")
    st.sidebar.caption(f"De {data_min.strftime('%d/%m/%Y')} até {data_max.strftime('%d/%m/%Y')}")

    data_inicio = st.sidebar.date_input(
        "Data inicial",
        value=data_min,
        min_value=data_min,
        max_value=data_max,
        format="DD/MM/YYYY"
    )

    data_fim = st.sidebar.date_input(
        "Data final",
        value=data_max,
        min_value=data_min,
        max_value=data_max,
        format="DD/MM/YYYY"
    )

    df_filtrado = df.copy()

    if agente_selecionado:
        df_filtrado = df_filtrado[df_filtrado["agente_sucesso"].isin(agente_selecionado)]

    if busca:
        termo = busca.strip().lower()
        df_filtrado = df_filtrado[
            df_filtrado["nome"].str.lower().str.contains(termo, na=False) |
            df_filtrado["matricula"].str.lower().str.contains(termo, na=False)
        ]

    if data_inicio and data_fim:
        inicio = pd.Timestamp(min(data_inicio, data_fim))
        fim = pd.Timestamp(max(data_inicio, data_fim))
        df_filtrado = df_filtrado[df_filtrado["data"].between(inicio, fim)]

    return df_filtrado


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
        "agente_sucesso",
        "status_monitoria",
        "link_monitoria"
    ]
].rename(columns={
    "data_formatada": "Data",
    "nome": "Nome",
    "matricula": "Matrícula",
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

# Exportação sem a coluna arquivo_origem
csv_export = (
    df_filtrado.drop(columns=["data_formatada", "arquivo_origem"], errors="ignore")
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