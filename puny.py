import argparse
from itertools import combinations, product

HOMOGLYPHS = {
    'a': ['а', 'ɑ', 'ⱥ'],  # Cirílico, IPA
    'e': ['е', 'ė', 'ë'],   # Cirílico, diacríticos
    'i': ['і', 'ǐ', 'ı'],   # Cirílico, latino
    'o': ['о', 'ø', 'õ'],   # Cirílico, diacríticos
    'y': ['у', 'ү', 'ÿ'],   # Cirílico, diacríticos
    'c': ['с', 'ċ', 'č'],   # Cirílico, diacríticos
    'm': ['м', 'ṃ'],        # Cirílico, diacríticos
    't': ['т', 'ţ'],        # Cirílico, diacríticos
    's': ['ѕ', 'š'],        # Cirílico, diacríticos
    'n': ['ñ', 'ń'],        # Diacríticos
    'g': ['ɡ', 'ğ'],        # IPA, diacríticos
    'u': ['μ', 'ü'],        # Grego, diacríticos
    'd': ['ð', 'đ'],        # Islandês, diacríticos
}

def generate_deceptive_links(domain, tld, max_substitutions=1):
    domain_chars = list(domain)
    replaceable = [i for i, c in enumerate(domain) if c in HOMOGLYPHS]
    results = []
    
    # Ajusta substituições máximas para o possível
    actual_max = min(max_substitutions, len(replaceable))
    if actual_max < 1:
        return results  # Sem caracteres substituíveis

    for count in range(1, actual_max + 1):
        for positions in combinations(replaceable, count):
            replacements = []
            for pos in positions:
                original = domain_chars[pos]
                replacements.append([(pos, g) for g in HOMOGLYPHS[original]])
            
            for combo in product(*replacements):
                modified = domain_chars.copy()
                for pos, glyph in combo:
                    modified[pos] = glyph
                fake_domain = ''.join(modified)
                try:
                    punycode = f"{fake_domain}.{tld}".encode('idna').decode()
                except UnicodeEncodeError:
                    continue  # Ignora caracteres não codificáveis
                results.append((f"{fake_domain}.{tld}", punycode))
                
    return sorted(set(results))  # Remove duplicatas e ordena

def generate_html(output_file, links):
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Punycode Demo (Educational)</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .warning {{ color: red; font-weight: bold; }}
        a {{ margin: 10px 0; display: block; }}
        .punycode {{ color: #666; font-size: 0.8em; }}
    </style>
</head>
<body>
    <div class="warning">WARNING: For educational purposes only. Do not use maliciously.</div>
    <h3>Visually similar links ({count} variations):</h3>
    {links}
</body>
</html>""".format(
        count=len(links),
        links='\n'.join(
            [f'<a href="http://{puny}" title="Punycode: {puny}">{display}<br><span class="punycode">{puny}</span></a>' 
             for display, puny in links]
        )
    )

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    parser = argparse.ArgumentParser(description='Educational Punycode Demo')
    parser.add_argument('domain', help='Base domain (e.g., "example")')
    parser.add_argument('tld', help='TLD (e.g., "com")')
    parser.add_argument('-o', '--output', default='links.html',
                      help='Output HTML file name (default: links.html)')
    parser.add_argument('-m', '--max-substitutions', type=int, default=1,
                      help='Maximum character substitutions (default: 1)')
    parser.add_argument('-p', '--print', action='store_true',
                      help='Print UTF-8 variations to terminal')
    args = parser.parse_args()

    links = generate_deceptive_links(
        args.domain.lower(),
        args.tld.lower(),
        args.max_substitutions
    )
    
    print(f"\nGenerated {len(links)} deceptive link variations")
    
    if args.print:
        print("\nUTF-8 Variations:")
        for i, (display, _) in enumerate(links, 1):
            print(f"{i}. {display}")
        print()

    if len(links) > 0:
        print(f"Output saved to {args.output}")
        generate_html(args.output, links)
    else:
        print("No variations possible - check input domain and substitution settings")

if __name__ == "__main__":
    main()
