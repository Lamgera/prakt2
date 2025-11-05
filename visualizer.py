import argparse
import sys

def create_parser():
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации графа зависимостей для менеджера пакетов"
    )
    parser.add_argument(
        "--package",
        required=True,
        help="Имя анализируемого пакета"
    )
    parser.add_argument(
        "--repo-url",
        required=True,
        help="URL-адрес репозитория или путь к файлу тестового репозитория"
    )
    parser.add_argument(
        "--repo-mode",
        required=True,
        help="Режим работы с тестовым репозиторием"
    )
    parser.add_argument(
        "--output-file",
        required=True,
        help="Имя сгенерированного файла с изображением графа"
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        required=True,
        help="Максимальная глубина анализа зависимостей"
    )
    parser.add_argument(
        "--filter",
        required=True,
        help="Подстрока для фильтрации пакетов"
    )
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    print("package:", args.package)
    print("repo_url:", args.repo_url)
    print("repo_mode:", args.repo_mode)
    print("output_file:", args.output_file)
    print("max_depth:", args.max_depth)
    print("filter:", args.filter)

    errors = []
    if not args.package:
        errors.append("Параметр --package не может быть пустым")
    if not args.repo_url:
        errors.append("Параметр --repo-url не может быть пустым")
    if not args.repo_mode:
        errors.append("Параметр --repo-mode не может быть пустым")
    if not args.output_file:
        errors.append("Параметр --output-file не может быть пустым")
    if args.max_depth is None or args.max_depth < 0:
        errors.append("Параметр --max-depth должен быть неотрицательным целым числом")
    if not args.filter:
        errors.append("Параметр --filter не может быть пустым")

    if errors:
        for error in errors:
            print(f"Ошибка: {error}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()