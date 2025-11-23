import streamlit as st
import pandas as pd
import pickle
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="🎬 Recomendador de Películas",
    page_icon="🎬",
    layout="wide"
)

# Cargar datos
@st.cache_resource
def load_data():
    """Carga el modelo y los datos"""
    try:
        with open('movie_similarity.pkl', 'rb') as f:
            similarity_matrix = pickle.load(f)
        with open('movies_data.pkl', 'rb') as f:
            movies = pickle.load(f)
        return similarity_matrix, movies
    except FileNotFoundError:
        st.error("⚠️ No se encontraron los archivos del modelo. Asegúrate de ejecutar el notebook del modelo primero.")
        return None, None

# Función de recomendación
def get_recommendations(movie_ids, similarity_matrix, movies, n=10):
    """
    Obtiene recomendaciones basadas en múltiples películas
    
    Args:
        movie_ids: Lista de IDs de películas
        similarity_matrix: Matriz de similitud
        movies: DataFrame con información de películas
        n: Número de recomendaciones
    
    Returns:
        DataFrame con recomendaciones
    """
    # Calcular score promedio de similitud para cada película
    all_scores = []
    
    for movie_id in movie_ids:
        if movie_id in similarity_matrix.columns:
            scores = similarity_matrix[movie_id]
            all_scores.append(scores)
    
    if not all_scores:
        return pd.DataFrame()
    
    # Promediar scores
    avg_scores = pd.concat(all_scores, axis=1).mean(axis=1)
    
    # Remover películas ya seleccionadas
    avg_scores = avg_scores[~avg_scores.index.isin(movie_ids)]
    
    # Top N
    top_movies = avg_scores.sort_values(ascending=False).head(n)
    
    # Crear DataFrame con resultados
    recommendations = pd.DataFrame({
        'item_id': top_movies.index,
        'score': top_movies.values
    })
    
    # Agregar información de películas
    recommendations = recommendations.merge(
        movies[['item_id', 'title']], 
        on='item_id',
        how='left'
    )
    
    return recommendations[['title', 'score']]

# Cargar datos
similarity_matrix, movies = load_data()

# Si los datos se cargaron correctamente
if similarity_matrix is not None and movies is not None:
    
    # Título principal
    st.title("🎬 Sistema de Recomendación de Películas")
    st.markdown("### Basado en Collaborative Filtering")
    
    st.markdown("---")
    
    # Descripción
    st.markdown("""
    **¿Cómo funciona?**
    1. Selecciona algunas películas que te gusten de la lista
    2. El sistema analizará tus preferencias
    3. Te mostrará películas similares que podrían interesarte
    
    *El modelo fue entrenado con el dataset MovieLens 100K*
    """)
    
    st.markdown("---")
    
    # Selector de películas
    st.subheader("🎯 Paso 1: Selecciona tus películas favoritas")
    
    # Crear lista de películas para el selector
    movie_list = movies.sort_values('title')['title'].tolist()
    
    selected_movies = st.multiselect(
        "Escoge al menos 3 películas que te gusten:",
        options=movie_list,
        help="Puedes seleccionar múltiples películas usando el menú desplegable"
    )
    
    # Mostrar películas seleccionadas
    if selected_movies:
        st.success(f"✅ Has seleccionado {len(selected_movies)} película(s)")
        
        # Mostrar en columnas
        cols = st.columns(min(len(selected_movies), 3))
        for idx, movie in enumerate(selected_movies):
            with cols[idx % 3]:
                st.write(f"🎬 {movie}")
    
    st.markdown("---")
    
    # Botón de recomendación
    if st.button("🚀 Obtener Recomendaciones", type="primary", use_container_width=True):
        
        if len(selected_movies) < 1:
            st.warning("⚠️ Por favor selecciona al menos 1 película")
        else:
            with st.spinner("🔍 Analizando tus preferencias..."):
                
                # Obtener IDs de las películas seleccionadas
                selected_ids = []
                for movie_title in selected_movies:
                    movie_id = movies[movies['title'] == movie_title]['item_id'].values
                    if len(movie_id) > 0:
                        selected_ids.append(movie_id[0])
                
                # Obtener recomendaciones
                recommendations = get_recommendations(
                    selected_ids, 
                    similarity_matrix, 
                    movies, 
                    n=10
                )
                
                if len(recommendations) > 0:
                    st.success("✅ ¡Recomendaciones generadas!")
                    
                    st.subheader("🎯 Top 10 Películas Recomendadas para Ti:")
                    
                    # Mostrar recomendaciones
                    for idx, row in recommendations.iterrows():
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            st.markdown(f"### {idx+1}. {row['title']}")
                        
                        with col2:
                            score_percentage = row['score'] * 100
                            st.metric("Match", f"{score_percentage:.0f}%")
                        
                        st.markdown("---")
                    
                    # Información adicional
                    st.info("""
                    💡 **Nota:** El porcentaje de "Match" indica qué tan similares son estas películas 
                    a las que seleccionaste. Un mayor porcentaje significa mayor similitud.
                    """)
                    
                else:
                    st.error("❌ No se pudieron generar recomendaciones. Intenta con otras películas.")
    
    # Sidebar con información
    st.sidebar.title("ℹ️ Información del Sistema")
    st.sidebar.markdown("""
    **Algoritmo:** Item-Based Collaborative Filtering
    
    **Dataset:** MovieLens 100K
    - 100,000 calificaciones
    - 1,682 películas
    - 943 usuarios
    
    **Desarrollado por:** Esteban Almitrani
    
    **Proyecto Integrador Final**
    Ciencia de Datos e IA
    """)
    
    # Estadísticas
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Estadísticas")
    st.sidebar.metric("Películas en el sistema", len(movies))
    st.sidebar.metric("Películas disponibles para recomendar", similarity_matrix.shape[0])

else:
    st.error("❌ Error al cargar el modelo. Verifica que los archivos del modelo existan en la carpeta 'src/'")


# streamlit run app.py