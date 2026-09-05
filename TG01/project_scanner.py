import ast
from pathlib import Path

import pathspec
import yaml


def get_module_docstring(filepath: Path) -> str:
    """Извлекает докстринг уровня модуля из Python-файла через AST."""
    if filepath.suffix != '.py':
        return "TODO: Описать назначение файла"
    
    try:
        source = filepath.read_text(encoding='utf-8')
        tree = ast.parse(source)
        doc = ast.get_docstring(tree)
        
        if doc:
            return " ".join(doc.strip().split())
        return "TODO: Добавить docstring в файл"
        
    except (SyntaxError, UnicodeDecodeError):
        return "TODO: Ошибка парсинга файла"

def load_gitignore(root_path: Path) -> pathspec.PathSpec:
    """
    Считывает .gitignore и возвращает объект для проверки путей.
    Добавляет базовые системные папки, даже если их нет в gitignore.
    """
    gitignore_path = root_path / '.gitignore'
    # Базовая защита на случай, если .gitignore пустой или отсутствует
    patterns = ['.git/', '__pycache__/', '.idea/', '.vscode/'] 
    
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            patterns.extend(f.readlines())
            
    # 'gitwildmatch' — это стандартный синтаксис парсинга Git
    return pathspec.PathSpec.from_lines('gitwildmatch', patterns)

def build_tree(path: Path, root_path: Path, ignore_spec: pathspec.PathSpec) -> dict | None:
    """
    Рекурсивно обходит директорию, фильтруя файлы по .gitignore
    и извлекая описания из докстрингов (включая __init__.py для папок).
    """
    # Получаем относительный путь (например 'app/routes.py' вместо '/full/path/app/routes.py')
    rel_path = str(path.relative_to(root_path))
    
    # Чтобы gitignore корректно применял правила для папок (например 'venv/'), 
    # добавляем слэш на конце при проверке директорий.
    check_path = f"{rel_path}/" if path.is_dir() else rel_path
    
    # Если путь в игнор-листе (и это не корень проекта) — отбрасываем весь узел
    if rel_path != "." and ignore_spec.match_file(check_path):
        return None

    # --- Определение описания (Description) ---
    if path.is_file():
        description = get_module_docstring(path)
    else:
        # Для директорий ищем __init__.py
        init_file = path / '__init__.py'
        if init_file.exists():
            description = get_module_docstring(init_file)
        else:
            description = "TODO: Описать назначение директории"

    # --- Сборка узла ---
    node = {
        "name": path.name if rel_path != "." else root_path.name,
        "is_directory": path.is_dir(),
        "description": description,
    }

    if path.is_dir():
        children = []
        for child in sorted(path.iterdir()):
            # Рекурсивно собираем дочерние элементы
            child_node = build_tree(child, root_path, ignore_spec)
            if child_node:  # Если не None (т.е. не отсеяно gitignore)
                children.append(child_node)
        
        if children:
            node["children"] = children
            
    return node

def generate_yaml_manifest(project_path: str, output_yaml: str, project_name: str):
    """Точка входа. Читает настройки и сохраняет итоговый YAML."""
    root_path = Path(project_path).resolve()
    
    if not root_path.exists() or not root_path.is_dir():
        raise ValueError(f"Путь {project_path} не существует.")

    # 1. Загружаем правила исключений
    ignore_spec = load_gitignore(root_path)
    
    # 2. Строим дерево
    tree = build_tree(root_path, root_path, ignore_spec)
    
    manifest = {
        "project_name": project_name,
        "root": tree
    }
    
    with open(output_yaml, 'w', encoding='utf-8') as f:
        yaml.dump(manifest, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    
    print(f"Манифест успешно сгенерирован: {output_yaml}")

if __name__ == "__main__":
    generate_yaml_manifest(
        project_path=".", 
        output_yaml="architecture_template.yaml",
        project_name="b2b_saas_mvp"
    )