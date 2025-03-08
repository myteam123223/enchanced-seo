# Script para ejecutar el Analizador SEO con API de Google
from enhanced_seo_analyzer import EnhancedSEOAnalyzer

def main():
    # Crear una instancia del analizador
    analyzer = EnhancedSEOAnalyzer()
    
    # Solicitar URLs al usuario
    print("Analizador SEO Avanzado con API de Google Custom Search")
    print("------------------------------------------------------")
    print("Ingresa las URLs de los sitios a analizar (una por línea).")
    print("El esquema (https:// o http://) se añadirá automáticamente si no lo incluyes.")
    print("Presiona Enter con una línea vacía para finalizar la lista.")
    
    urls = []
    while True:
        url = input("URL: ").strip()
        if not url:
            break
        urls.append(url)
    
    if not urls:
        print("Debes ingresar al menos una URL para analizar.")
        return
    
    # Solicitar palabra clave objetivo
    target_keyword = input("\n¿Deseas analizar una palabra clave específica? (deja en blanco para omitir): ").strip()
    
    # Seleccionar idioma
    language = input("\nIdioma del contenido (es/en) [es]: ").strip().lower() or 'es'
    
    # Seleccionar formato de salida
    output_format = input("\nFormato de salida (text/excel/json) [excel]: ").strip().lower() or 'excel'
    
    print("\nIniciando análisis, esto puede tardar varios minutos...")
    print("Se utilizará la API de Google Custom Search para determinar el posicionamiento.")
    print("También se generarán keywords relacionadas automáticamente.")
    print("Tip: Para mejores resultados, prueba con sitios web como www.wikipedia.org, www.python.org, etc.")
    
    try:
        # Realizar el análisis
        results = analyzer.compare_competitors(urls, target_keyword, language=language)
        
        # Generar informe
        report_file = analyzer.generate_report(results, output_format=output_format)
        print(f"\nInforme generado: {report_file}")
        
        # Generar visualizaciones
        print("\nCreando visualizaciones...")
        charts = analyzer.visualize_results(results)
        
        for chart_type, chart_path in charts.items():
            if chart_path:
                print(f"- {chart_type.replace('_', ' ').title()}: {chart_path}")
        
        print(f"\n¡Análisis completado! Todos los archivos se guardaron en la carpeta: {analyzer.results_dir}")
        
        # Información adicional sobre las nuevas características
        if target_keyword:
            print(f"\nSe ha incluido:")
            print(f"- Análisis de posicionamiento para la keyword '{target_keyword}'")
            print(f"- Generación de {len(results.get('related_keywords', []))} keywords relacionadas")
            print(f"- Gráficos comparativos de posicionamiento en buscadores")
            print(f"- Consulta a la API de Google Custom Search para obtener posiciones reales")
        
        # Proporcionar sugerencias si hay pocos resultados
        if len(results['individual_results']) < len(urls):
            print("\nAlgunas URLs no pudieron ser analizadas correctamente.")
            print("Sugerencias de URLs para probar:")
            print("- https://www.wordpress.org")
            print("- https://www.wikipedia.org")
            print("- https://www.python.org")
            print("- https://www.mozilla.org")
        
    except Exception as e:
        print(f"\nError durante el análisis: {str(e)}")
        print("Por favor, verifica que las URLs sean correctas y accesibles.")
        print("Sugerencia: Prueba con sitios web populares que no bloqueen el scraping.")

if __name__ == "__main__":
    main()
