import argparse
import sys
import json
import os

def parse_args():
    parser = argparse.ArgumentParser(
        prog="DependencyGraphVisualizer",
        description="Этап 4: прямые и обратные зависимости."
    )
    parser.add_argument('--package', required=True)
    parser.add_argument('--repo-url', required=True)
    parser.add_argument('--repo-mode', required=True, choices=['remote', 'local'])
    parser.add_argument('--output-file', required=True)
    parser.add_argument('--max-depth', type=int, required=True)
    parser.add_argument(
    '--filter',
    nargs='?',
    const='',
    default='',
    help="Подстрока для фильтрации пакетов (по умолчанию: '').")

    args = parser.parse_args()

    if args.max_depth < 0:
        print("--max-depth не может быть отрицательным.", file=sys.stderr)
        sys.exit(1)
    if args.repo_mode == 'remote':
        print("Режим 'remote' не поддерживается. Используйте 'local'.", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.repo_url):
        print(f"Файл репозитория не найден: {args.repo_url}", file=sys.stderr)
        sys.exit(1)
    return args

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

def build_reverse_graph(forward_graph):
    reverse = {node: [] for node in forward_graph}
    for pkg, deps in forward_graph.items():
        for dep in deps:
            if dep in reverse:
                reverse[dep].append(pkg)
            else:
                reverse[dep] = [pkg]
    return reverse

def bfs_by_levels(graph, start_pkg, max_depth, filter_substring):
    if start_pkg not in graph:
        return {}

    visited = set([start_pkg])
    result = {}

    def process_level(nodes, depth):
        if depth > max_depth or not nodes:
            return
        next_level = []
        for pkg in nodes:
            raw_neighbors = graph[pkg] 
            filtered = [
                n for n in raw_neighbors
                if not filter_substring or filter_substring not in n
            ]
            result[pkg] = filtered
            for n in filtered:
                if n not in visited:
                    visited.add(n)
                    next_level.append(n)
        process_level(next_level, depth + 1)

    process_level([start_pkg], 0)
    return result

def main():
    args = parse_args()
    repo = load_repo(args.repo_url)

    forward_graph = repo_to_forward_graph(repo)

    all_packages = set(forward_graph.keys())
    if args.package not in all_packages:
        print(f"Пакет '{args.package}' не найден в репозитории.", file=sys.stderr)
        sys.exit(1)

    direct = bfs_by_levels(
        graph=forward_graph,
        start_pkg=args.package,
        max_depth=args.max_depth,
        filter_substring=args.filter
    )

    print("Прямые зависимости (пакет -> [от чего зависит]):")
    for pkg, deps in direct.items():
        print(f"{pkg} -> {deps}")

    print()

    reverse_graph = build_reverse_graph(forward_graph)
    reverse = bfs_by_levels(
        graph=reverse_graph,
        start_pkg=args.package,
        max_depth=args.max_depth,
        filter_substring=args.filter
    )

    print("Обратные зависимости (пакет <- [в ком используется]):")
    for pkg, dependents in reverse.items():
        print(f"{pkg} <- {dependents}")

if __name__ == "__main__":
    main()