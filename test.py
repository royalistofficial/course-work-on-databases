import os

def delete_initial_file(start_dir):
    for root, dirs, files in os.walk(start_dir):
        if '0001_initial.py' in files:
            file_path = os.path.join(root, '0001_initial.py')
            os.remove(file_path)
            print(f'{file_path} удален.')

    
    print('Процесс удаления завершен.')

# Получаем текущую директорию, где расположен скрипт
current_dir = os.path.dirname(__file__)
delete_initial_file(current_dir)
