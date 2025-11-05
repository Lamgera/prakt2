import argparse
import sys
import json
import os
import subprocess

def parse_args():
    parser = argparse.ArgumentParser(
        prog="DependencyGraphVisualizer",
        description="Этап 5: визуализация графа зависимостей в формате D2/SVG."
    )
    parser.add_argument('--package', required=True)
    parser.add_argument('--repo-url', required=True)
    parser.add_argument('--repo-mode', required=True, choices=['remote', 'local'])
    parser.add_argument('--output-file', required=True)  # например, graph.svg
    parser.add_argument('--max-depth', type=int, required=True)
    parser.add_argument(
        '--filter',
        nargs='?',
        const='',
        default='',
        help="Подстрока для фильтрации пакетов."
    )
    return parser.parse_args()

def load_repo(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for pkg, info in data.items():
            if not isinstance(info.get("dependencies", []), list):
                raise ValueError(f"Некорректный формат зависимостей для пакета '{pkg}'")
        return data
    except (json.JSONDecodeError, ValueError, OSError) as e:
        print(f"Ошибка чтения репозитория: {e}", file=sys.stderr)
        sys.exit(1)

def repo_to_forward_graph(repo):
    graph = {}
    for pkg, info in repo.items():
        graph[pkg] = info.get("dependencies", [])
    for deps in repo.values():
        for d in deps:
            if d not in graph:
                graph[d] = []
    return graph

def bfs_collect_edges(graph, start_pkg, max_depth, filter_substring):
    edges = set()
    visited_global = set()

    def visit(pkg, depth, path_set):
        if depth > max_depth or pkg in path_set:
            return
        if pkg in visited_global and depth >= getattr(visit, '_depths', {}).get(pkg, max_depth + 1):
            return

        if not hasattr(visit, '_depths'):
            visit._depths = {}
        if pkg not in visit._depths or depth < visit._depths[pkg]:
            visit._depths[pkg] = depth

        visited_global.add(pkg)

        if pkg not in graph:
            return

        raw_deps = graph[pkg]
        filtered_deps = [
            d for d in raw_deps
            if not filter_substring or filter_substring not in d
        ]

        for dep in filtered_deps:
            edges.add((pkg, dep))

        new_path = path_set | {pkg}
        for dep in filtered_deps:
            visit(dep, depth + 1, new_path)

    visit(start_pkg, 0, set())
    return edges

def generate_d2_code(edges):
    lines = []
    for src, dst in sorted(edges):
        lines.append(f"{src} -> {dst}")
    return "\n".join(lines)

def render_d2_to_svg(d2_content, output_svg):
    d2_file = output_svg.replace('.svg', '.d2')
    try:
        with open(d2_file, 'w', encoding='utf-8') as f:
            f.write(d2_content)
        result = subprocess.run(
            ['d2', d2_file, output_svg],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Ошибка генерации SVG через d2:\n{result.stderr}", file=sys.stderr)
            print("Сохранён только .d2 файл:", d2_file, file=sys.stderr)
            return False
        return True
    except FileNotFoundError:
        print("Инструмент 'd2' не найден.", file=sys.stderr)
        print("Сохранён только .d2 файл:", d2_file, file=sys.stderr)
        return False
    except Exception as e:
        print(f"Ошибка при рендеринге SVG: {e}", file=sys.stderr)
        return False

def main():
    args = parse_args()
    if args.repo_mode == 'remote':
        print("Режим 'remote' не поддерживается.", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.repo_url):
        print(f"Файл репозитория не найден: {args.repo_url}", file=sys.stderr)
        sys.exit(1)

    repo = load_repo(args.repo_url)
    graph = repo_to_forward_graph(repo)

    if args.package not in graph:
        print(f"Пакет '{args.package}' не найден.", file=sys.stderr)
        sys.exit(1)

    edges = bfs_collect_edges(
        graph=graph,
        start_pkg=args.package,
        max_depth=args.max_depth,
        filter_substring=args.filter
    )

    d2_code = generate_d2_code(edges)
    print("D2-код графа:")
    print(d2_code)
    print()

    success = render_d2_to_svg(d2_code, args.output_file)
    if success:
        print(f"SVG сохранён: {args.output_file}")
    else:
        d2_path = args.output_file.replace('.svg', '.d2')
        print(f"Файл D2 сохранён: {d2_path}")

if __name__ == "__main__":
    main()