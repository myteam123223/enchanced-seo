# Tokenizar y limpiar el texto
        words = re.findall(r'\b\w+\b', text.lower())
        words = [word for word in words if word.isalnum() and len(word) >= min_length and word not in stop_words]
        
        # Contar frecuencias
        word_freq = Counter(words)
        
        # Devolver las palabras más frecuentes
        return word_freq.most_common(top_n)
    
    def analyze_keyword_phrases(self, text, language='es', min_length=2, max_length=4, top_n=20):
        """Analiza frases clave (n-gramas) en el texto"""
        if not text:
            return []
            
        # Seleccionar stopwords según el idioma
        stop_words = self.get_language_stopwords(language)
        
        # Tokenizar y limpiar el texto
        words = re.findall(r'\b\w+\b', text.lower())
        words = [word for word in words if word.isalnum() and word not in stop_words]
        
        # Generar n-gramas
        phrases = []
        for n in range(min_length, max_length + 1):
            for i in range(len(words) - n + 1):
                phrases.append(' '.join(words[i:i+n]))
        
        # Contar frecuencias
        phrase_freq = Counter(phrases)
        
        # Devolver las frases más frecuentes
        return phrase_freq.most_common(top_n)
    
    def analyze_content_structure(self, seo_data):
        """Analiza la estructura del contenido"""
        structure_analysis = {
            'title_length': len(seo_data['title']),
            'meta_description_length': len(seo_data['meta_description']),
            'title': seo_data['title'],
            'meta_description': seo_data['meta_description'],
            'has_h1': len(seo_data['h1_tags']) > 0,
            'h1_count': len(seo_data['h1_tags']),
            'h2_count': len(seo_data['h2_tags']),
            'h3_count': len(seo_data['h3_tags']),
            'paragraph_count': len(seo_data['paragraphs']),
            'avg_paragraph_length': sum(len(p) for p in seo_data['paragraphs']) / len(seo_data['paragraphs']) if seo_data['paragraphs'] else 0,
            'internal_link_count': len(seo_data['internal_links']),
            'external_link_count': len(seo_data['external_links']),
            'image_count': len(seo_data['images']),
            'images_with_alt': sum(1 for img in seo_data['images'] if img.get('alt')),
            'schema_types': seo_data['schema_data'],
            'has_schema': len(seo_data['schema_data']) > 0,
            'h1_tags': seo_data['h1_tags'][:3] if seo_data['h1_tags'] else [],
            'h2_tags': seo_data['h2_tags'][:5] if seo_data['h2_tags'] else [],
        }
        return structure_analysis
    
    def compare_competitors(self, urls, target_keyword=None, language='es'):
        """Compara el contenido de múltiples competidores con enfoque en SEO"""
        results = []
        all_keywords = Counter()
        all_phrases = Counter()
        related_keywords = []
        
        # Si hay una keyword objetivo, generamos keywords relacionadas
        if target_keyword:
            related_keywords = self.generate_related_keywords(target_keyword, language)
        
        for url in urls:
            print(f"Analizando: {url}")
            seo_data = self.extract_content(url, target_keyword)
            
            if not seo_data:
                print(f"No se pudo analizar {url}, continuando con la siguiente URL")
                continue
                
            try:
                # Analizar palabras clave
                keywords = self.analyze_keywords(seo_data['main_content'], language)
                
                # Analizar frases clave
                phrases = self.analyze_keyword_phrases(seo_data['main_content'], language)
                
                # Analizar estructura
                structure = self.analyze_content_structure(seo_data)
                
                # Actualizar contadores globales
                for word, count in keywords:
                    all_keywords[word] += count
                    
                for phrase, count in phrases:
                    all_phrases[phrase] += count
                
                # Guardar resultados individuales
                result = {
                    'url': url,
                    'domain': seo_data.get('domain', urlparse(url).netloc),
                    'title': seo_data.get('title', ''),
                    'meta_description': seo_data.get('meta_description', ''),
                    'top_keywords': keywords[:10],
                    'top_phrases': phrases[:10],
                    'structure': structure
                }
                
                # Añadir análisis de keyword específica si se proporcionó
                if target_keyword and 'keyword_analysis' in seo_data:
                    result['keyword_analysis'] = seo_data['keyword_analysis']
                
                # Añadir posición en buscadores si está disponible
                if target_keyword and 'search_position' in seo_data:
                    result['search_position'] = seo_data['search_position']
                
                # Añadir keywords relacionadas si están disponibles
                if target_keyword and 'related_keywords' in seo_data:
                    result['related_keywords'] = seo_data['related_keywords']
                
                results.append(result)
            except Exception as e:
                print(f"Error al analizar {url}: {str(e)}")
                continue
            
            # Pausa entre solicitudes para evitar bloqueos
            time.sleep(2)
        
        # Calcular palabras y frases clave comunes entre competidores
        common_analysis = {
            'common_keywords': all_keywords.most_common(30),
            'common_phrases': all_phrases.most_common(20)
        }
        
        return {
            'individual_results': results,
            'common_analysis': common_analysis,
            'target_keyword': target_keyword,
            'related_keywords': related_keywords
        }
    
    def generate_report(self, comparison_results, output_format='excel'):
        """Genera un informe basado en los resultados del análisis"""
        if not comparison_results['individual_results']:
            print("No hay datos suficientes para generar un informe detallado.")
            print("Generando informe mínimo con la información disponible.")
            
            # Generar un informe mínimo
            output_file = f"{self.results_dir}/seo_analysis_minimal.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=== ANÁLISIS SEO BÁSICO ===\n\n")
                f.write("No se encontraron datos suficientes para un análisis completo.\n")
                f.write("Posibles razones:\n")
                f.write("- Las URLs no son accesibles\n")
                f.write("- El sitio bloquea el scraping\n")
                f.write("- Hubo errores al procesar el contenido\n\n")
                
                f.write("Recomendaciones:\n")
                f.write("- Intenta con otras URLs\n")
                f.write("- Verifica que los sitios estén en línea\n")
                f.write("- Usa sitios que no bloqueen la extracción de contenido\n")
            
            return output_file
            
        # Si llegamos aquí, hay al menos algunos datos para analizar
        domain_names = [result['domain'] for result in comparison_results['individual_results']]
        target_keyword = comparison_results.get('target_keyword')
        related_keywords = comparison_results.get('related_keywords', [])
        
        # Crear un resumen de estructura para comparación
        structure_data = []
        for result in comparison_results['individual_results']:
            data = {'domain': result['domain']}
            data.update(result['structure'])
            structure_data.append(data)
        
        structure_df = pd.DataFrame(structure_data)
        
        # Generar el informe según el formato solicitado
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        
        if output_format == 'json':
            # Guardar resultados como JSON
            output_file = f"{self.results_dir}/seo_analysis.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                # Convertir a un diccionario serializable
                serializable_results = {
                    'individual_results': [],
                    'common_analysis': comparison_results['common_analysis'],
                    'target_keyword': comparison_results.get('target_keyword'),
                    'related_keywords': related_keywords
                }
                
                # Procesar cada resultado individual
                for result in comparison_results['individual_results']:
                    serializable_result = {
                        'url': result['url'],
                        'domain': result['domain'],
                        'title': result['title'],
                        'meta_description': result['meta_description'],
                        'top_keywords': result['top_keywords'],
                        'top_phrases': result['top_phrases'],
                        'structure': result['structure']
                    }
                    
                    if 'keyword_analysis' in result:
                        serializable_result['keyword_analysis'] = result['keyword_analysis']
                    
                    if 'search_position' in result:
                        serializable_result['search_position'] = result['search_position']
                        
                    serializable_results['individual_results'].append(serializable_result)
                
                json.dump(serializable_results, f, ensure_ascii=False, indent=4)
            return output_file
            
        elif output_format in ['excel', 'xlsx']:
            # Guardar resultados en Excel
            output_file = f"{self.results_dir}/seo_analysis.xlsx"
            
            try:
                # Crear un writer de Excel
                with pd.ExcelWriter(output_file) as writer:
                    # Hoja de resumen
                    summary_data = []
                    for result in comparison_results['individual_results']:
                        domain_data = {
                            'Dominio': result['domain'],
                            'URL': result['url'],
                            'Título': result['title'],
                            'Meta Descripción': result['meta_description'],
                            'Longitud Título': len(result['title']),
                            'Longitud Meta Descripción': len(result['meta_description']),
                            'H1': result['structure']['h1_count'],
                            'H2': result['structure']['h2_count'],
                            'H3': result['structure']['h3_count'],
                            'Párrafos': result['structure']['paragraph_count'],
                            'Enlaces Internos': result['structure']['internal_link_count'],
                            'Enlaces Externos': result['structure']['external_link_count'],
                            'Imágenes': result['structure']['image_count'],
                            'Imágenes con Alt': result['structure']['images_with_alt'],
                            'Tiene Schema': 'Sí' if result['structure']['has_schema'] else 'No',
                            'Tipos de Schema': ', '.join(result['structure']['schema_types']),
                        }
                        
                        # Añadir análisis de keyword específica si está disponible
                        if target_keyword and 'keyword_analysis' in result:
                            keyword_analysis = result['keyword_analysis']
                            domain_data.update({
                                f'Keyword: {target_keyword}': 'Análisis',
                                'Keyword en Título': 'Sí' if keyword_analysis.get('in_title', False) else 'No',
                                'Keyword en Meta Desc': 'Sí' if keyword_analysis.get('in_meta_description', False) else 'No',
                                'Keyword en URL': 'Sí' if keyword_analysis.get('in_url', False) else 'No',
                                'Keyword en H1': 'Sí' if keyword_analysis.get('in_h1', False) else 'No',
                                'Keyword en H2': 'Sí' if keyword_analysis.get('in_h2', False) else 'No',
                                'Keyword en Primer Párrafo': 'Sí' if keyword_analysis.get('in_first_paragraph', False) else 'No',
                                'Keyword en Alt de Imágenes': 'Sí' if keyword_analysis.get('in_img_alt', False) else 'No',
                                'Keyword en Nombres de Imágenes': 'Sí' if keyword_analysis.get('in_img_filename', False) else 'No',
                                'Keyword en Enlaces Internos': 'Sí' if keyword_analysis.get('in_internal_links_text', False) else 'No',
                                'Conteo de Keyword': keyword_analysis.get('keyword_count', 0),
                                'Densidad de Keyword (%)': keyword_analysis.get('keyword_density', 0),
                                'Puntaje SEO (1-100)': keyword_analysis.get('seo_score', 0),
                            })
                            
                        # Añadir información de posicionamiento si está disponible
                        if target_keyword and 'search_position' in result:
                            position_data = result['search_position']
                            
                            # Determinar si se usó API real
                            api_used = position_data.get('api_used', False)
                            position_value = position_data.get('position', 'Desconocida')
                            
                            domain_data.update({
                                'Posición en Buscadores': position_value,
                                'Rango de Posición': position_data.get('position_range', 'N/A'),
                                'Confianza de la Estimación': position_data.get('confidence', 'N/A'),
                                'Top 10': 'Sí' if position_data.get('top_10', False) else 'No',
                                'Top 30': 'Sí' if position_data.get('top_30', False) else 'No',
                                'API Google Utilizada': 'Sí' if api_used else 'No'
                            })
                        
                        summary_data.append(domain_data)
                    
                    if summary_data:
                        summary_df = pd.DataFrame(summary_data)
                        summary_df.to_excel(writer, sheet_name='Resumen SEO', index=False)
                    else:
                        # Si no hay datos de resumen, crear una hoja vacía con mensaje
                        pd.DataFrame([{'Mensaje': 'No hay datos suficientes para el resumen'}]).to_excel(writer, sheet_name='Resumen SEO', index=False)
                    
                    # Hoja de estructura detallada
                    structure_df.to_excel(writer, sheet_name='Estructura', index=False)
                    
                    # Hoja de palabras clave comunes
                    common_keywords_df = pd.DataFrame(comparison_results['common_analysis']['common_keywords'], 
                                                    columns=['Palabra', 'Frecuencia'])
                    common_keywords_df.to_excel(writer, sheet_name='Keywords Comunes', index=False)
                    
                    # Hoja de frases comunes
                    common_phrases_df = pd.DataFrame(comparison_results['common_analysis']['common_phrases'], 
                                                columns=['Frase', 'Frecuencia'])
                    common_phrases_df.to_excel(writer, sheet_name='Frases Comunes', index=False)
                    
                    # Hoja de keywords relacionadas si hay keyword objetivo
                    if target_keyword and related_keywords:
                        related_kw_df = pd.DataFrame({'Keyword Relacionada': related_keywords})
                        related_kw_df.to_excel(writer, sheet_name='Keywords Relacionadas', index=False)
                    
                    # Hoja con posicionamiento en buscadores
                    if target_keyword:
                        position_data = []
                        for result in comparison_results['individual_results']:
                            if 'search_position' in result:
                                pos = result['search_position']
                                position_data.append({
                                    'Dominio': result['domain'],
                                    'URL': result['url'],
                                    'Posición Estimada': pos.get('position', 'Desconocida'),
                                    'Rango de Posición': pos.get('position_range', 'N/A'),
                                    'Confianza': pos.get('confidence', 'N/A'),
                                    'Top 10': 'Sí' if pos.get('top_10', False) else 'No',
                                    'Top 30': 'Sí' if pos.get('top_30', False) else 'No',
                                    'Top 100': 'Sí' if pos.get('top_100', False) else 'No',
                                    'API Google Utilizada': 'Sí' if pos.get('api_used', False) else 'No'
                                })
                        
                        if position_data:
                            position_df = pd.DataFrame(position_data)
                            position_df.to_excel(writer, sheet_name='Posicionamiento', index=False)
                    
                    # Hojas individuales para cada dominio
                    for result in comparison_results['individual_results']:
                        domain = result['domain']
                        safe_domain = ''.join(c for c in domain[:10] if c.isalnum())
                        
                        # Encabezados
                        headers_data = []
                        if result['structure'].get('h1_tags'):
                            for h1 in result['structure']['h1_tags']:
                                headers_data.append({'Tipo': 'H1', 'Texto': h1})
                        if result['structure'].get('h2_tags'):
                            for h2 in result['structure']['h2_tags']:
                                headers_data.append({'Tipo': 'H2', 'Texto': h2})
                        
                        if headers_data:
                            headers_df = pd.DataFrame(headers_data)
                            headers_df.to_excel(writer, sheet_name=f'{safe_domain}_Headers', index=False)
                        
                        # Keywords de este dominio
                        if result['top_keywords']:
                            domain_keywords_df = pd.DataFrame(result['top_keywords'], columns=['Palabra', 'Frecuencia'])
                            domain_keywords_df.to_excel(writer, sheet_name=f'{safe_domain}_Keywords', index=False)
                        
                        # Frases de este dominio
                        if result['top_phrases']:
                            domain_phrases_df = pd.DataFrame(result['top_phrases'], columns=['Frase', 'Frecuencia'])
                            domain_phrases_df.to_excel(writer, sheet_name=f'{safe_domain}_Frases', index=False)
                        
                        # Análisis específico de keyword si está disponible
                        if target_keyword and 'keyword_analysis' in result:
                            kw_analysis = result['keyword_analysis']
                            
                            # Datos generales
                            kw_general_data = [
                                {'Métrica': 'Keyword', 'Valor': target_keyword},
                                {'Métrica': 'Conteo de Keyword', 'Valor': kw_analysis.get('keyword_count', 0)},
                                {'Métrica': 'Densidad de Keyword (%)', 'Valor': kw_analysis.get('keyword_density', 0)},
                                {'Métrica': 'Keyword en Título', 'Valor': 'Sí' if kw_analysis.get('in_title', False) else 'No'},
                                {'Métrica': 'Keyword en Meta Descripción', 'Valor': 'Sí' if kw_analysis.get('in_meta_description', False) else 'No'},
                                {'Métrica': 'Keyword en URL', 'Valor': 'Sí' if kw_analysis.get('in_url', False) else 'No'},
                                {'Métrica': 'Keyword en H1', 'Valor': 'Sí' if kw_analysis.get('in_h1', False) else 'No'},
                                {'Métrica': 'Keyword en H2', 'Valor': 'Sí' if kw_analysis.get('in_h2', False) else 'No'},
                                {'Métrica': 'Keyword en Primer Párrafo', 'Valor': 'Sí' if kw_analysis.get('in_first_paragraph', False) else 'No'},
                                {'Métrica': 'Keyword en Atributos Alt', 'Valor': 'Sí' if kw_analysis.get('in_img_alt', False) else 'No'},
                                {'Métrica': 'Keyword en Nombres de Archivos', 'Valor': 'Sí' if kw_analysis.get('in_img_filename', False) else 'No'},
                                {'Métrica': 'Keyword en Texto de Enlaces', 'Valor': 'Sí' if kw_analysis.get('in_internal_links_text', False) else 'No'},
                                {'Métrica': 'Puntaje SEO (1-100)', 'Valor': kw_analysis.get('seo_score', 0)},
                            ]
                            
                            # Añadir datos de posicionamiento si están disponibles
                            if 'search_position' in result:
                                pos = result['search_position']
                                kw_general_data.extend([
                                    {'Métrica': 'Posición Estimada', 'Valor': pos.get('position', 'Desconocida')},
                                    {'Métrica': 'Rango de Posición', 'Valor': pos.get('position_range', 'N/A')},
                                    {'Métrica': 'Confianza', 'Valor': pos.get('confidence', 'N/A')},
                                    {'Métrica': 'En Top 10', 'Valor': 'Sí' if pos.get('top_10', False) else 'No'},
                                    {'Métrica': 'En Top 30', 'Valor': 'Sí' if pos.get('top_30', False) else 'No'},
                                    {'Métrica': 'API Google Utilizada', 'Valor': 'Sí' if pos.get('api_used', False) else 'No'}
                                ])
                            
                            kw_general_df = pd.DataFrame(kw_general_data)
                            kw_general_df.to_excel(writer, sheet_name=f'{safe_domain}_KW', index=False)
                            
                            # Keywords similares
                            if kw_analysis.get('similar_keywords'):
                                similar_kw_data = []
                                for kw, sim in kw_analysis['similar_keywords']:
                                    count = kw_analysis['similar_keywords_counts'].get(kw, 0)
                                    similar_kw_data.append({
                                        'Keyword Similar': kw,
                                        'Similitud (%)': sim,
                                        'Frecuencia': count
                                    })
                                
                                similar_kw_df = pd.DataFrame(similar_kw_data)
                                similar_kw_df.to_excel(writer, sheet_name=f'{safe_domain}_KWSim', index=False)
                
                return output_file
            except Exception as e:
                print(f"Error al generar Excel: {str(e)}")
                # En caso de error, crear un informe de texto
                output_file = f"{self.results_dir}/seo_analysis_error.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Error al generar informe Excel: {str(e)}\n")
                    f.write("Se recomienda utilizar el formato 'text' o 'json' en su lugar.")
                return output_file
            
        else:  # Formato de texto por defecto
            output_file = f"{self.results_dir}/seo_analysis.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=== ANÁLISIS SEO AVANZADO ===\n\n")
                
                # Escribir resumen general
                f.write("== DOMINIOS ANALIZADOS ==\n")
                for domain in domain_names:
                    f.write(f"- {domain}\n")
                f.write("\n")
                
                if target_keyword:
                    f.write(f"== KEYWORD OBJETIVO: {target_keyword} ==\n\n")
                    
                    # Escribir keywords relacionadas
                    if related_keywords:
                        f.write("== KEYWORDS RELACIONADAS ==\n")
                        for kw in related_keywords:
                            f.write(f"- {kw}\n")
                        f.write("\n")
                
                # Escribir palabras clave comunes
                f.write("== PALABRAS CLAVE COMUNES ==\n")
                for word, count in comparison_results['common_analysis']['common_keywords'][:15]:
                    f.write(f"{word}: {count}\n")
                f.write("\n")
                
                # Escribir frases clave comunes
                f.write("== FRASES CLAVE COMUNES ==\n")
                for phrase, count in comparison_results['common_analysis']['common_phrases'][:10]:
                    f.write(f"{phrase}: {count}\n")
                f.write("\n")
                
                # Posicionamiento general
                if target_keyword:
                    f.write("== POSICIONAMIENTO PARA KEYWORD ==\n")
                    for result in comparison_results['individual_results']:
                        if 'search_position' in result:
                            pos = result['search_position']
                            api_used = 'Sí' if pos.get('api_used', False) else 'No'
                            f.write(f"{result['domain']}:\n")
                            f.write(f"  - Posición estimada: {pos.get('position', 'Desconocida')}\n")
                            f.write(f"  - Rango: {pos.get('position_range', 'N/A')}\n")
                            f.write(f"  - Confianza: {pos.get('confidence', 'N/A')}\n")
                            f.write(f"  - Top 10: {'Sí' if pos.get('top_10', False) else 'No'}\n")
                            f.write(f"  - Top 30: {'Sí' if pos.get('top_30', False) else 'No'}\n")
                            f.write(f"  - API Google utilizada: {api_used}\n")
                    f.write("\n")
                
                # Escribir análisis individual
                f.write("== ANÁLISIS INDIVIDUAL ==\n")
                for result in comparison_results['individual_results']:
                    f.write(f"\n--- {result['domain']} ---\n")
                    f.write(f"URL: {result['url']}\n")
                    f.write(f"Título: {result['title']}\n")
                    f.write(f"Meta Descripción: {result['meta_description']}\n")
                    
                    f.write("\nEstructura:\n")
                    f.write(f"- H1: {result['structure']['h1_count']}\n")
                    f.write(f"- H2: {result['structure']['h2_count']}\n")
                    f.write(f"- H3: {result['structure']['h3_count']}\n")
                    f.write(f"- Párrafos: {result['structure']['paragraph_count']}\n")
                    f.write(f"- Enlaces Internos: {result['structure']['internal_link_count']}\n")
                    f.write(f"- Enlaces Externos: {result['structure']['external_link_count']}\n")
                    f.write(f"- Imágenes: {result['structure']['image_count']}\n")
                    f.write(f"- Imágenes con Alt: {result['structure']['images_with_alt']}\n")
                    
                    f.write("\nSchema.org:\n")
                    if result['structure']['has_schema']:
                        f.write(f"- Tipos: {', '.join(result['structure']['schema_types'])}\n")
                    else:
                        f.write("- No se detectaron datos estructurados\n")
                    
                    f.write("\nPalabras clave principales:\n")
                    for word, count in result['top_keywords']:
                        f.write(f"- {word}: {count}\n")
                    
                    f.write("\nFrases clave principales:\n")
                    for phrase, count in result['top_phrases']:
                        f.write(f"- {phrase}: {count}\n")
                    
                    # Escribir análisis de keyword específica si está disponible
                    if target_keyword and 'keyword_analysis' in result:
                        kw = result['keyword_analysis']
                        f.write(f"\nAnálisis de keyword: {target_keyword}\n")
                        f.write(f"- Conteo: {kw.get('keyword_count', 0)}\n")
                        f.write(f"- Densidad: {kw.get('keyword_density', 0)}%\n")
                        f.write(f"- En título: {'Sí' if kw.get('in_title', False) else 'No'}\n")
                        f.write(f"- En meta descripción: {'Sí' if kw.get('in_meta_description', False) else 'No'}\n")
                        f.write(f"- En URL: {'Sí' if kw.get('in_url', False) else 'No'}\n")
                        f.write(f"- En H1: {'Sí' if kw.get('in_h1', False) else 'No'}\n")
                        f.write(f"- En H2: {'Sí' if kw.get('in_h2', False) else 'No'}\n")
                        f.write(f"- En primer párrafo: {'Sí' if kw.get('in_first_paragraph', False) else 'No'}\n")
                        f.write(f"- En alt de imágenes: {'Sí' if kw.get('in_img_alt', False) else 'No'}\n")
                        f.write(f"- En nombres de archivos: {'Sí' if kw.get('in_img_filename', False) else 'No'}\n")
                        f.write(f"- En texto de enlaces: {'Sí' if kw.get('in_internal_links_text', False) else 'No'}\n")
                        f.write(f"- Puntaje SEO: {kw.get('seo_score', 0)}/100\n")
                        
                        f.write("\nKeywords similares:\n")
                        for similar, score in kw.get('similar_keywords', []):
                            count = kw.get('similar_keywords_counts', {}).get(similar, 0)
                            f.write(f"- {similar}: similitud {score}%, frecuencia {count}\n")
                    
                    # Escribir información de posicionamiento si está disponible
                    if target_keyword and 'search_position' in result:
                        pos = result['search_position']
                        api_used = 'Sí' if pos.get('api_used', False) else 'No'
                        f.write(f"\nPosicionamiento en buscadores para '{target_keyword}':\n")
                        f.write(f"- Posición estimada: {pos.get('position', 'Desconocida')}\n")
                        f.write(f"- Rango de posición: {pos.get('position_range', 'N/A')}\n")
                        f.write(f"- Confianza de la estimación: {pos.get('confidence', 'N/A')}\n")
                        f.write(f"- En Top 10: {'Sí' if pos.get('top_10', False) else 'No'}\n")
                        f.write(f"- En Top 30: {'Sí' if pos.get('top_30', False) else 'No'}\n")
                        f.write(f"- En Top 100: {'Sí' if pos.get('top_100', False) else 'No'}\n")
                        f.write(f"- API Google utilizada: {api_used}\n")
                    
                    f.write("\n")
            
            return output_file
    
    def visualize_results(self, comparison_results):
        """Visualiza los resultados del análisis"""
        # Verificar si hay datos para visualizar
        if not comparison_results['individual_results']:
            print("No hay datos suficientes para crear visualizaciones.")
            return {}
            
        # Crear figuras para visualización
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        charts = {}
        
        try:
            # 1. Gráfico de barras para palabras clave comunes
            plt.figure(figsize=(12, 6))
            top_keywords = comparison_results['common_analysis']['common_keywords'][:10]
            
            if top_keywords:
                words, counts = zip(*top_keywords)
                plt.bar(words, counts)
                plt.title('Palabras clave más comunes')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                keywords_chart = f"{self.results_dir}/keywords.png"
                plt.savefig(keywords_chart)
                charts['keywords_chart'] = keywords_chart
            
            # 2. Gráfico comparativo de estructura de contenido
            if len(comparison_results['individual_results']) > 0:
                plt.figure(figsize=(12, 8))
                structure_data = []
                domains = []
                
                for result in comparison_results['individual_results']:
                    domains.append(result['domain'])
                    structure_data.append([
                        result['structure'].get('paragraph_count', 0),
                        result['structure'].get('h1_count', 0) + result['structure'].get('h2_count', 0) + result['structure'].get('h3_count', 0),
                        result['structure'].get('internal_link_count', 0),
                        result['structure'].get('external_link_count', 0),
                        result['structure'].get('image_count', 0)
                    ])
                
                structure_df = pd.DataFrame(structure_data, 
                                        index=domains,
                                        columns=['Párrafos', 'Encabezados', 'Enlaces Internos', 'Enlaces Externos', 'Imágenes'])
                
                structure_df.plot(kind='bar', figsize=(12, 6))
                plt.title('Comparación de estructura de contenido')
                plt.ylabel('Cantidad')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                structure_chart = f"{self.results_dir}/structure.png"
                plt.savefig(structure_chart)
                charts['structure_chart'] = structure_chart
                
                # 3. Gráfico específico de análisis de keyword si está disponible
                target_keyword = comparison_results.get('target_keyword')
                if target_keyword:
                    kw_data = []
                    domains = []
                    
                    for result in comparison_results['individual_results']:
                        if 'keyword_analysis' in result:
                            domains.append(result['domain'])
                            kw_analysis = result['keyword_analysis']
                            kw_data.append([
                                kw_analysis.get('keyword_density', 0),
                                kw_analysis.get('keyword_count', 0),
                                kw_analysis.get('seo_score', 0)
                            ])
                    
                    if kw_data and domains:
                        plt.figure(figsize=(12, 6))
                        kw_df = pd.DataFrame(kw_data, 
                                            index=domains,
                                            columns=['Densidad (%)', 'Conteo', 'Puntaje SEO'])
                        
                        ax = kw_df.plot(kind='bar', figsize=(12, 6), secondary_y=['Puntaje SEO'])
                        plt.title(f'Análisis de keyword: {target_keyword}')
                        plt.ylabel('Densidad (%) / Conteo')
                        ax.right_ax.set_ylabel('Puntaje SEO (1-100)')
                        plt.xticks(rotation=45, ha='right')
                        plt.tight_layout()
                        keyword_chart = f"{self.results_dir}/keyword_analysis.png"
                        plt.savefig(keyword_chart)
                        charts['keyword_analysis_chart'] = keyword_chart
                
                # 4. Gráfico de posicionamiento en buscadores
                if target_keyword:
                    position_data = []
                    domains = []
                    
                    for result in comparison_results['individual_results']:
                        if 'search_position' in result:
                            position = result['search_position']
                            pos_value = position.get('position', 0)
                            
                            # Si no es un entero, tratar de convertirlo o usar un valor por defecto
                            if not isinstance(pos_value, int):
                                try:
                                    if isinstance(pos_value, str) and pos_value.startswith('>'):
                                        # Para ">100", usar 100
                                        pos_value = 100
                                    else:
                                        pos_value = int(pos_value)
                                except:
                                    pos_value = 100  # Valor por defecto
                            
                            domains.append(result['domain'])
                            position_data.append(pos_value)
                    
                    if position_data and domains:
                        plt.figure(figsize=(12, 6))
                        # Invertir el eje y para que las mejores posiciones estén arriba
                        plt.bar(domains, position_data)
                        plt.gca().invert_yaxis()  # Invertir para que posición 1 esté arriba
                        plt.axhline(y=10, color='green', linestyle='--', label='Top 10')
                        plt.axhline(y=30, color='orange', linestyle='--', label='Top 30')
                        plt.axhline(y=50, color='red', linestyle='--', label='Top 50')
                        plt.title(f'Posicionamiento para keyword: {target_keyword}')
                        plt.ylabel('Posición en buscadores')
                        plt.xlabel('Dominio')
                        plt.xticks(rotation=45, ha='right')
                        plt.legend()
                        plt.tight_layout()
                        position_chart = f"{self.results_dir}/position_analysis.png"
                        plt.savefig(position_chart)
                        charts['position_chart'] = position_chart
                        
                # 5. Gráfico de keywords relacionadas
                if comparison_results.get('related_keywords'):
                    related_keywords = comparison_results['related_keywords']
                    plt.figure(figsize=(12, 10))
                    
                    # Limitar a las primeras 15 keywords relacionadas para mejor visualización
                    if len(related_keywords) > 15:
                        related_keywords = related_keywords[:15]
                        
                    # Crear un gráfico de barras horizontal para las keywords relacionadas
                    y_pos = range(len(related_keywords))
                    plt.barh(y_pos, [1] * len(related_keywords), color='skyblue')
                    plt.yticks(y_pos, related_keywords)
                    plt.title(f'Keywords relacionadas con: {target_keyword}')
                    plt.xlabel('Sugerencia para creación de contenido')
                    plt.tight_layout()
                    related_chart = f"{self.results_dir}/related_keywords.png"
                    plt.savefig(related_chart)
                    charts['related_keywords_chart'] = related_chart
                    
        except Exception as e:
            print(f"Error al crear visualizaciones: {str(e)}")
            
        return charts
                        f.write(f"import requests
from bs4 import BeautifulSoup, Comment
import re
from collections import Counter, defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import time
from urllib.parse import urlparse, quote_plus
import os
import json
import datetime
import urllib.robotparser
from difflib import SequenceMatcher
import random

class EnhancedSEOAnalyzer:
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        self.headers = {'User-Agent': self.user_agent}
        
        # Configuración de API de Google
        self.google_api_key = "AIzaSyC2VRH52aBn8miMvStkyOEMAPEcAMYx1gE"
        self.google_cx = "0fc0215ffaa1a49d9"  # ID de tu motor de búsqueda personalizado
        
        # Definición manual de stopwords
        self.spanish_stopwords = set(['a', 'al', 'algo', 'algunas', 'algunos', 'ante', 'antes', 'como', 'con', 'contra',
            'cual', 'cuando', 'de', 'del', 'desde', 'donde', 'durante', 'e', 'el', 'ella',
            'ellas', 'ellos', 'en', 'entre', 'era', 'eramos', 'eran', 'eres', 'es', 'esa',
            'esas', 'ese', 'eso', 'esos', 'esta', 'estaba', 'estado', 'estamos', 'estan',
            'estar', 'estas', 'este', 'esto', 'estos', 'estoy', 'etc', 'fue', 'fueron',
            'fui', 'fuimos', 'ha', 'has', 'hasta', 'hay', 'he', 'hemos', 'hube', 'hubo',
            'la', 'las', 'le', 'les', 'lo', 'los', 'me', 'mi', 'mia', 'mias', 'mientras',
            'mio', 'mios', 'mis', 'mucho', 'muchos', 'muy', 'ni', 'no', 'nos', 'nosotras',
            'nosotros', 'nuestra', 'nuestras', 'nuestro', 'nuestros', 'o', 'os', 'otra',
            'otras', 'otro', 'otros', 'para', 'pero', 'poco', 'por', 'porque', 'que',
            'quien', 'quienes', 'se', 'sea', 'sean', 'segun', 'ser', 'si', 'sido', 'siendo',
            'sin', 'sobre', 'sois', 'somos', 'son', 'soy', 'su', 'sus', 'suya', 'suyas',
            'suyo', 'suyos', 'tambien', 'tanto', 'te', 'teneis', 'tenemos', 'tener', 'tengo',
            'ti', 'tiene', 'tienen', 'tu', 'tus', 'tuya', 'tuyas', 'tuyo', 'tuyos', 'un',
            'una', 'uno', 'unos', 'vosotras', 'vosotros', 'vuestra', 'vuestras', 'vuestro',
            'vuestros', 'y', 'ya', 'yo'])
            
        self.english_stopwords = set(['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and',
            'any', 'are', 'as', 'at', 'be', 'because', 'been', 'before', 'being',
            'below', 'between', 'both', 'but', 'by', 'could', 'did', 'do', 'does',
            'doing', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had',
            'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him',
            'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself',
            'me', 'more', 'most', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on',
            'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own',
            'same', 'she', 'should', 'so', 'some', 'such', 'than', 'that', 'the', 'their',
            'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those',
            'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we', 'were',
            'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with', 'would',
            'you', 'your', 'yours', 'yourself', 'yourselves'])
        
        # Crear directorio para guardar resultados con timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = f'seo_analysis_{timestamp}'
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
            
    def get_language_stopwords(self, language='es'):
        """Devuelve el conjunto de stopwords según el idioma especificado"""
        if language.lower() in ['es', 'spanish']:
            return self.spanish_stopwords
        else:
            return self.english_stopwords
    
    def is_allowed_by_robots(self, url, respect_robots=False):
        """Verifica si el scraping está permitido por robots.txt"""
        if not respect_robots:
            return True
            
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{base_url}/robots.txt")
            rp.read()
            
            return rp.can_fetch(self.user_agent, url)
        except Exception as e:
            print(f"Error al verificar robots.txt ({str(e)}), continuando con el análisis")
            # Si hay algún error al verificar, asumimos que está permitido
            return True
    
    def get_search_position(self, domain, keyword, language='es', max_results=100):
        """
        Obtiene la posición de búsqueda para un dominio y keyword específicos
        usando la API de Google Custom Search.
        """
        try:
            print(f"Analizando posición para: {domain} con keyword '{keyword}'...")
            
            # Si tenemos API key, usamos la API real
            if self.google_api_key:
                # URL base para la API de Google Custom Search
                search_url = "https://www.googleapis.com/customsearch/v1"
                
                # Parámetros de la consulta
                params = {
                    'key': self.google_api_key,
                    'cx': self.google_cx,  # Motor de búsqueda personalizado
                    'q': keyword,
                    'num': 10,  # Máximo 10 resultados por consulta
                    'gl': 'es' if language.lower() in ['es', 'spanish'] else 'us',  # Localización geográfica
                    'hl': language
                }
                
                position = None
                total_checked = 0
                
                # Consultamos hasta obtener el máximo de resultados (en páginas de 10)
                for start_index in range(1, max_results + 1, 10):
                    params['start'] = start_index
                    
                    try:
                        response = requests.get(search_url, params=params)
                        response.raise_for_status()
                        search_results = response.json()
                        
                        if 'items' in search_results:
                            items = search_results['items']
                            
                            # Verificar cada resultado
                            for i, item in enumerate(items):
                                result_url = item.get('link', '')
                                result_domain = urlparse(result_url).netloc
                                
                                # Normalizar dominios (quitar www si existe)
                                result_domain = result_domain.replace('www.', '')
                                domain_normalized = domain.replace('www.', '')
                                
                                if result_domain == domain_normalized:
                                    position = start_index + i
                                    break
                            
                            if position:
                                break
                                
                            total_checked += len(items)
                            
                            # Si ya verificamos suficientes resultados, detenemos
                            if total_checked >= max_results:
                                break
                        else:
                            # No hay más resultados
                            break
                            
                        # Pausa para respetar límites de API
                        time.sleep(1)
                    except Exception as e:
                        print(f"Error en consulta de API (página {start_index//10 + 1}): {str(e)}")
                        break
                
                # Si encontramos la posición
                if position:
                    confidence = "Alta"
                    position_range = f"{position}"
                    
                    return {
                        'position': position,
                        'position_range': position_range,
                        'confidence': confidence,
                        'top_10': position <= 10,
                        'top_30': position <= 30,
                        'top_100': position <= 100,
                        'api_used': True
                    }
                else:
                    # Si no encontramos el sitio en los resultados
                    return {
                        'position': '>100',
                        'position_range': '>100',
                        'confidence': 'Alta',
                        'top_10': False,
                        'top_30': False,
                        'top_100': False,
                        'api_used': True
                    }
            
            # Si no hay API key, usamos simulación
            else:
                # Generamos un hash basado en el dominio y la keyword para simular consistencia
                domain_hash = sum(ord(c) for c in domain)
                keyword_hash = sum(ord(c) for c in keyword)
                combined_hash = domain_hash + keyword_hash
                
                # Usamos el hash para generar una posición semipredecible
                random.seed(combined_hash)
                position = random.randint(1, max_results)
                
                # Añadimos alguna incertidumbre pero manteniendo cierta estabilidad
                if position <= 10:  # Sitios que parecen estar bien posicionados
                    confidence = "Media"
                    position_range = f"{position}-{position+2}"
                elif position <= 30:  # Sitios con posición media
                    confidence = "Media"
                    position_range = f"{position-3}-{position+3}"
                else:  # Sitios mal posicionados
                    confidence = "Baja"
                    position_range = f"{position-5}-{position+5}"
                
                return {
                    'position': position,
                    'position_range': position_range,
                    'confidence': confidence,
                    'top_10': position <= 10,
                    'top_30': position <= 30,
                    'top_100': position <= 100,
                    'api_used': False
                }
        except Exception as e:
            print(f"Error al obtener posición SEO: {str(e)}")
            return {
                'position': 'Desconocida',
                'position_range': 'N/A',
                'confidence': 'N/A',
                'top_10': False,
                'top_30': False,
                'top_100': False,
                'error': str(e),
                'api_used': False
            }
    
    def generate_related_keywords(self, keyword, language='es'):
        """
        Genera keywords relacionadas basadas en la keyword principal.
        Utiliza patrones comunes y combinaciones lógicas.
        """
        if not keyword:
            return []
            
        related_keywords = []
        
        # Patrones comunes para español e inglés
        patterns_es = [
            "mejor {keyword}",
            "{keyword} online",
            "comprar {keyword}",
            "{keyword} barato",
            "{keyword} precio",
            "{keyword} vs",
            "como {keyword}",
            "{keyword} para principiantes",
            "{keyword} profesional",
            "{keyword} gratis",
            "ventajas de {keyword}",
            "{keyword} cerca de mi",
            "{keyword} opiniones",
            "alternativas a {keyword}",
            "{keyword} tutorial"
        ]
        
        patterns_en = [
            "best {keyword}",
            "{keyword} online",
            "buy {keyword}",
            "cheap {keyword}",
            "{keyword} price",
            "{keyword} vs",
            "how to {keyword}",
            "{keyword} for beginners",
            "{keyword} professional",
            "{keyword} free",
            "benefits of {keyword}",
            "{keyword} near me",
            "{keyword} reviews",
            "alternatives to {keyword}",
            "{keyword} tutorial"
        ]
        
        # Seleccionar patrones según el idioma
        patterns = patterns_es if language.lower() in ['es', 'spanish'] else patterns_en
        
        # Generar keywords relacionadas
        for pattern in patterns:
            related_keywords.append(pattern.format(keyword=keyword))
        
        # Agregar variantes adicionales
        keyword_parts = keyword.split()
        if len(keyword_parts) > 1:
            # Para keywords compuestas, crear variaciones de orden
            for i in range(len(keyword_parts)):
                parts_copy = keyword_parts.copy()
                first_part = parts_copy.pop(i)
                
                # Mover una palabra al inicio
                new_keyword = first_part + " " + " ".join(parts_copy)
                if new_keyword != keyword:
                    related_keywords.append(new_keyword)
        
        # Cuando tenemos una sola palabra, podemos agregar algunos modificadores comunes
        else:
            modifiers_es = ["nuevo", "mejor", "bueno", "fácil", "rápido", "simple", "económico", "profesional", "avanzado"]
            modifiers_en = ["new", "best", "good", "easy", "quick", "simple", "cheap", "professional", "advanced"]
            
            modifiers = modifiers_es if language.lower() in ['es', 'spanish'] else modifiers_en
            
            for modifier in modifiers:
                related_keywords.append(f"{modifier} {keyword}")
                related_keywords.append(f"{keyword} {modifier}")
        
        # Eliminar duplicados y devolver lista final
        return list(set(related_keywords))
    
    def extract_content(self, url, target_keyword=None):
        """Extrae el contenido de una URL con análisis SEO avanzado"""
        try:
            # Añadir esquema si no existe
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                print(f"URL modificada a: {url}")
                
            # Verificar si está permitido el scraping (cambia False a True para respetar robots.txt)
            if not self.is_allowed_by_robots(url, respect_robots=False):
                print(f"El scraping no está permitido para {url} según robots.txt, pero continuamos el análisis")
                # Continuamos con el análisis en lugar de retornar None
                
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer datos estructurados (Schema.org) con manejo de errores
            try:
                schema_data = self.extract_schema_data(soup)
            except Exception as e:
                print(f"Error al extraer datos estructurados: {str(e)}")
                schema_data = []
            
            # Eliminar comentarios HTML
            for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
                comment.extract()
            
            # Eliminar scripts, estilos y otros elementos no relevantes
            for tag in soup(['script', 'style', 'iframe']):
                try:
                    tag.extract()
                except:
                    pass
            
            # Extraer datos SEO fundamentales con manejo de errores
            try:
                title = soup.title.text.strip() if soup.title else ''
            except:
                title = ''
                
            try:
                meta_description = soup.find('meta', attrs={'name': 'description'})
                meta_description = meta_description['content'] if meta_description else ''
            except:
                meta_description = ''
            
            # Extraer elementos estructurales con manejo de errores
            try:
                h1_tags = [h1.text.strip() for h1 in soup.find_all('h1')]
            except:
                h1_tags = []
                
            try:
                h2_tags = [h2.text.strip() for h2 in soup.find_all('h2')]
            except:
                h2_tags = []
                
            try:
                h3_tags = [h3.text.strip() for h3 in soup.find_all('h3')]
            except:
                h3_tags = []
            
            # Extraer párrafos de contenido
            try:
                paragraphs = [p.text.strip() for p in soup.find_all('p') if len(p.text.strip()) > 20]
                first_paragraph = paragraphs[0] if paragraphs else ''
            except:
                paragraphs = []
                first_paragraph = ''
            
            # Extraer imágenes con sus atributos
            images = []
            try:
                for img in soup.find_all('img'):
                    try:
                        src = img.get('src', '')
                        alt = img.get('alt', '')
                        # Obtener el nombre de archivo de la imagen
                        filename = src.split('/')[-1].split('?')[0] if src else ''
                        
                        images.append({
                            'src': src,
                            'alt': alt,
                            'filename': filename
                        })
                    except:
                        continue
            except:
                images = []
            
            # Extraer enlaces internos y externos
            internal_links = []
            external_links = []
            
            try:
                domain = urlparse(url).netloc
                for a in soup.find_all('a', href=True):
                    try:
                        href = a['href']
                        text = a.text.strip()
                        
                        # Normalizar enlaces relativos
                        if href.startswith('/'):
                            parsed_url = urlparse(url)
                            href = f"{parsed_url.scheme}://{parsed_url.netloc}{href}"
                        
                        # Clasificar como interno o externo
                        if domain in href or href.startswith('/'):
                            internal_links.append({
                                'href': href,
                                'text': text
                            })
                        else:
                            external_links.append({
                                'href': href,
                                'text': text
                            })
                    except:
                        continue
            except:
                internal_links = []
                external_links = []
            
            # Extraer el contenido principal para análisis textual
            main_content = ' '.join(paragraphs)
            
            # Crear estructura completa de datos
            seo_data = {
                'url': url,
                'domain': domain,
                'title': title,
                'meta_description': meta_description,
                'h1_tags': h1_tags,
                'h2_tags': h2_tags,
                'h3_tags': h3_tags,
                'first_paragraph': first_paragraph,
                'paragraphs': paragraphs,
                'images': images,
                'internal_links': internal_links,
                'external_links': external_links,
                'schema_data': schema_data,
                'main_content': main_content,
                'full_html': response.text
            }
            
            # Realizar análisis específico de keywords si se proporcionó una
            if target_keyword:
                try:
                    seo_data['keyword_analysis'] = self.analyze_keyword_usage(seo_data, target_keyword)
                    
                    # Analizar posición en buscadores
                    seo_data['search_position'] = self.get_search_position(domain, target_keyword)
                    
                    # Generar keywords relacionadas
                    seo_data['related_keywords'] = self.generate_related_keywords(target_keyword)
                except Exception as e:
                    print(f"Error en análisis de keyword: {str(e)}")
                    seo_data['keyword_analysis'] = {}
                    seo_data['search_position'] = {}
                    seo_data['related_keywords'] = []
            
            return seo_data
        
        except Exception as e:
            print(f"Error al extraer contenido de {url}: {str(e)}")
            return None
    
    def extract_schema_data(self, soup):
        """Extrae datos estructurados (Schema.org) de la página"""
        schema_types = []
        
        # Buscar JSON-LD
        try:
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    if script.string:
                        data = json.loads(script.string)
                        # Extraer el tipo de schema 
                        if isinstance(data, dict):
                            if '@type' in data:
                                # Manejar '@type' que puede ser string o lista
                                if isinstance(data['@type'], str):
                                    schema_types.append(data['@type'])
                                elif isinstance(data['@type'], list):
                                    schema_types.extend(data['@type'])
                            elif '@graph' in data:
                                for item in data['@graph']:
                                    if '@type' in item:
                                        if isinstance(item['@type'], str):
                                            schema_types.append(item['@type'])
                                        elif isinstance(item['@type'], list):
                                            schema_types.extend(item['@type'])
                except Exception:
                    continue
        except Exception:
            pass
        
        # Buscar Microdata
        try:
            itemtypes = soup.find_all(itemtype=True)
            for item in itemtypes:
                try:
                    if 'schema.org' in item['itemtype']:
                        schema_type = item['itemtype'].split('/')[-1]
                        schema_types.append(schema_type)
                except Exception:
                    continue
        except Exception:
            pass
        
        # Buscar RDFa
        try:
            rdfa_elements = soup.find_all(property=True)
            for elem in rdfa_elements:
                try:
                    if 'schema.org' in elem.get('property', ''):
                        schema_types.append('RDFa')
                        break
                except Exception:
                    continue
        except Exception:
            pass
        
        return list(set(schema_types))  # Eliminar duplicados
    
    def similarity_score(self, a, b):
        """Calcula la similitud entre dos cadenas de texto"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def find_similar_keywords(self, keyword, text, min_similarity=0.8):
        """Encuentra variantes y términos similares a una keyword"""
        if not text:
            return []
            
        words = re.findall(r'\b\w+\b', text.lower())
        unique_words = set(words)
        
        similar_words = []
        for word in unique_words:
            # Omitir palabras muy cortas
            if len(word) < 4:
                continue
                
            similarity = self.similarity_score(keyword, word)
            if similarity >= min_similarity and word != keyword.lower():
                similar_words.append((word, similarity))
        
        # Ordenar por similitud descendente
        return sorted(similar_words, key=lambda x: x[1], reverse=True)
    
    def analyze_keyword_usage(self, seo_data, keyword):
        """Analiza el uso de una keyword específica en la página"""
        if not keyword:
            return {}
            
        keyword = keyword.lower()
        result = {}
        
        # 1. Keyword en el título
        result['in_title'] = keyword in seo_data['title'].lower() if seo_data['title'] else False
        
        # 2. Keyword en meta descripción
        result['in_meta_description'] = keyword in seo_data['meta_description'].lower() if seo_data['meta_description'] else False
        
        # 3. Keyword en URL
        result['in_url'] = keyword in seo_data['url'].lower() if seo_data['url'] else False
        
        # 4. Keyword en H1
        result['in_h1'] = any(keyword in h1.lower() for h1 in seo_data['h1_tags']) if seo_data['h1_tags'] else False
        
        # 5. Keyword en H2
        result['in_h2'] = any(keyword in h2.lower() for h2 in seo_data['h2_tags']) if seo_data['h2_tags'] else False
        
        # 6. Keyword en primer párrafo
        result['in_first_paragraph'] = keyword in seo_data['first_paragraph'].lower() if seo_data['first_paragraph'] else False
        
        # 7. Keyword en atributos alt de imágenes
        result['in_img_alt'] = any(keyword in img['alt'].lower() for img in seo_data['images'] if img.get('alt')) if seo_data['images'] else False
        
        # 8. Keyword en nombres de archivo de imágenes
        result['in_img_filename'] = any(keyword in img['filename'].lower() for img in seo_data['images'] if img.get('filename')) if seo_data['images'] else False
        
        # 9. Keyword en texto ancla de enlaces internos
        result['in_internal_links_text'] = any(keyword in link['text'].lower() for link in seo_data['internal_links'] if link.get('text')) if seo_data['internal_links'] else False
        
        # 10. Densidad de la keyword en el contenido principal
        main_content = seo_data['main_content'].lower() if seo_data['main_content'] else ""
        word_count = len(re.findall(r'\b\w+\b', main_content))
        keyword_count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', main_content))
        
        result['keyword_count'] = keyword_count
        result['keyword_density'] = round(keyword_count / word_count * 100, 2) if word_count > 0 else 0
        
        # 11. Encontrar keywords similares y sinónimos (LSI)
        try:
            similar_keywords = self.find_similar_keywords(keyword, main_content)
            result['similar_keywords'] = [(word, round(sim * 100)) for word, sim in similar_keywords[:10]]
        except Exception:
            result['similar_keywords'] = []
        
        # 12. Calcular frecuencia de variantes/similares
        similar_keywords_counts = {}
        for word, _ in result['similar_keywords']:
            try:
                count = len(re.findall(r'\b' + re.escape(word) + r'\b', main_content))
                similar_keywords_counts[word] = count
            except Exception:
                similar_keywords_counts[word] = 0
        
        result['similar_keywords_counts'] = similar_keywords_counts
        
        # 13. Calcular puntaje SEO para la keyword (simple)
        seo_score = 0
        if result['in_title']: seo_score += 20
        if result['in_meta_description']: seo_score += 10
        if result['in_url']: seo_score += 15
        if result['in_h1']: seo_score += 15
        if result['in_h2']: seo_score += 10
        if result['in_first_paragraph']: seo_score += 10
        if result['in_img_alt']: seo_score += 5
        if result['in_img_filename']: seo_score += 5
        if result['in_internal_links_text']: seo_score += 5
        
        # Ajustar por densidad (penalizar si es muy alta o muy baja)
        density = result['keyword_density']
        if 0.5 <= density <= 2.5:
            seo_score += 5
        elif density > 2.5:
            seo_score -= min(10, int(density - 2.5) * 2)  # Penalizar keyword stuffing
        
        result['seo_score'] = min(100, seo_score)  # Máximo 100 puntos
        
        return result
    
    def analyze_keywords(self, text, language='es', min_length=3, top_n=30):
        """Analiza las palabras clave más frecuentes en un texto"""
        if not text:
            return []
        
        # Seleccionar stopwords según el idioma
        stop_words = self.get_language_stopwords(language)
        
        # Tokenizar y limpiar el texto
        words = re.findall(r'\b\w+\b', text.lower())
        words = [word for word in words if word.isalnum() and len(word) >= min_length and word not in stop_words]
