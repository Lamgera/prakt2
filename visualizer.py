import argparse
import sys
import json
import os

def parse_args():
    parser = argparse.ArgumentParser(
        prog="DependencyGraphVisualizer",
        description="Этап 3: построение графа зависимостей с фильтрацией и обработкой циклов."
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
    help="Подстрока для фильтрации пакетов (по умолчанию: '')."
)

    args = parser.parse_args()

    if args.max_depth < 0:
        print("--max-depth не может быть отрицательным.", file=sys.stderr)
        sys.exit(1)
    if args.repo_mode == 'remote':
        print("Режим 'remote' не поддерживается. Используйте 'local' с тестовым JSON-файлом.", file=sys.stderr)
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

def bfs_collect(repo, start_pkg, max_depth, filter_substring):
    graph = {}
    visited = set()
    visited.add(start_pkg)
    level_nodes = [start_pkg]

    def process_level(nodes, depth):
        if depth > max_depth or not nodes:
            return
        next_level = []
        for pkg in nodes:
            if pkg not in repo:
                continue
            raw_deps = repo[pkg].get("dependencies", [])
            filtered_deps = [
                d for d in raw_deps
                if not filter_substring or filter_substring not in d
            ]
            graph[pkg] = filtered_deps
            for dep in filtered_deps:
                if dep not in visited:
                    visited.add(dep)
                    next_level.append(dep)
        process_level(next_level, depth + 1)

    process_level(level_nodes, 0)
    return graph

def main():
    args = parse_args()
    repo = load_repo(args.repo_url)

    if args.package not in repo:
        print(f"Пакет '{args.package}' не найден в репозитории.", file=sys.stderr)
        sys.exit(1)

    graph = bfs_collect(
        repo=repo,
        start_pkg=args.package,
        max_depth=args.max_depth,
        filter_substring=args.filter
    )

    print("Граф зависимостей:")
    for pkg, deps in graph.items():
        print(f"{pkg} -> {deps}")

if __name__ == "__main__":
    main()