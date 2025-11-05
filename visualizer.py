import argparse
import sys
import json
import os

def parse_args():
    parser = argparse.ArgumentParser(
        prog="DependencyGraphVisualizer",
        description="Этап 2: сбор данных о прямых зависимостях."
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

    try:
        args = parser.parse_args()
        if args.max_depth < 0:
            print("--max-depth не может быть отрицательным.", file=sys.stderr)
            sys.exit(1)
        if args.repo_mode == 'remote':
            print("Режим 'remote' не поддерживается на этапе 2 (только локальный тестовый репозиторий).", file=sys.stderr)
            sys.exit(1)
        if not os.path.isfile(args.repo_url):
            print(f"Файл репозитория не найден: {args.repo_url}", file=sys.stderr)
            sys.exit(1)
        return args
    except SystemExit:
        raise
    except Exception as e:
        print(f"Ошибка аргументов: {e}", file=sys.stderr)
        sys.exit(1)

def load_repo(repo_path):
    try:
        with open(repo_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Некорректный JSON в файле репозитория: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Не удалось прочитать файл репозитория: {e}", file=sys.stderr)
        sys.exit(1)

def get_direct_dependencies(package_name, repo_data):
    if package_name not in repo_data:
        print(f"Пакет '{package_name}' не найден в репозитории.", file=sys.stderr)
        sys.exit(1)
    deps = repo_data[package_name].get("dependencies", [])
    if not isinstance(deps, list):
        print(f"Некорректный формат зависимостей для пакета '{package_name}'.", file=sys.stderr)
        sys.exit(1)
    return deps

def main():
    args = parse_args()
    repo_data = load_repo(args.repo_url)
    direct_deps = get_direct_dependencies(args.package, repo_data)

    print("Прямые зависимости:")
    for dep in direct_deps:
        print(dep)

if __name__ == "__main__":
    main()