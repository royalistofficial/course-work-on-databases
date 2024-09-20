import sqlite3
import matplotlib.pyplot as plt
import random
import time

def find_record_by_id(record_id):
    start_time = time.time()
    cursor.execute('SELECT * FROM test WHERE id = ?', (record_id,))
    record = cursor.fetchone()
    end_time = time.time()
    elapsed_time = end_time - start_time
    return record, elapsed_time

def find_record_by_unique_text(unique_text):
    start_time = time.time()
    cursor.execute('SELECT * FROM test WHERE unique_text = ?', (unique_text,))
    record = cursor.fetchone()
    end_time = time.time()
    elapsed_time = end_time - start_time
    return record, elapsed_time

def find_record_by_mask(mask):
    start_time = time.time()
    cursor.execute('SELECT * FROM test WHERE not_unique_text LIKE ?', (mask,))
    record = cursor.fetchone()
    end_time = time.time()
    elapsed_time = end_time - start_time
    return record, elapsed_time

def add_record(unique_text, not_unique_text):
    start_time = time.time()
    cursor.execute('''
        INSERT INTO test (unique_text, not_unique_text) VALUES (?, ?);
    ''', (unique_text, not_unique_text))
    conn.commit() 
    end_time = time.time()
    elapsed_time = end_time - start_time
    return elapsed_time

def add_records(records):
    start_time = time.time()
    cursor.executemany('''
        INSERT INTO test (unique_text, not_unique_text) VALUES (?, ?);
    ''', records)
    conn.commit()
    end_time = time.time()
    elapsed_time = end_time - start_time
    return elapsed_time

def update_record(record_id, new_unique_text, new_not_unique_text):
    start_time = time.time()
    cursor.execute('''
        UPDATE test
        SET unique_text = ?, not_unique_text = ?
        WHERE id = ?;
    ''', (new_unique_text, new_not_unique_text, record_id))
    conn.commit() 
    end_time = time.time()
    elapsed_time = end_time - start_time
    return elapsed_time

def update_record_by_unique_text(unique_text, new_not_unique_text):
    start_time = time.time()
    cursor.execute('''
        UPDATE test
        SET not_unique_text = ?
        WHERE unique_text = ?;
    ''', (new_not_unique_text, unique_text))
    conn.commit()
    end_time = time.time()
    elapsed_time = end_time - start_time
    return elapsed_time

def delete_record_by_id(record_id):
    start_time = time.time()
    cursor.execute('''
        DELETE FROM test
        WHERE id = ?;
    ''', (record_id,))
    conn.commit() 
    end_time = time.time()
    elapsed_time = end_time - start_time
    return elapsed_time

def delete_record_by_unique_text(unique_text):
    start_time = time.time()
    cursor.execute('''
        DELETE FROM test
        WHERE unique_text = ?;
    ''', (unique_text,))
    conn.commit() 
    cursor.execute('VACUUM')
    conn.commit()
    end_time = time.time()
    elapsed_time = end_time - start_time
    return elapsed_time

def delete_records_by_id(record_ids):
    start_time = time.time()
    placeholders = ', '.join('?' for _ in record_ids)  
    cursor.execute(f'''
        DELETE FROM test
        WHERE id IN ({placeholders});
    ''', record_ids)
    conn.commit()
    end_time = time.time()
    elapsed_time = end_time - start_time
    return elapsed_time

def vacuum_delete_records_by_id(record_ids):
    placeholders = ', '.join('?' for _ in record_ids)  
    cursor.execute(f'''
        DELETE FROM test
        WHERE id IN ({placeholders});
    ''', record_ids)
    conn.commit()

    start_time = time.time()
    cursor.execute('VACUUM')
    conn.commit()
    end_time = time.time()
    elapsed_time = end_time - start_time
    return elapsed_time

def delete_all_except_last_n(n):
    cursor.execute('SELECT id FROM test ORDER BY id DESC LIMIT ?', (n,))
    ids_to_keep = {row[0] for row in cursor.fetchall()}

    if ids_to_keep:
        placeholders = ', '.join('?' for _ in ids_to_keep) 
        cursor.execute(f'''
            DELETE FROM test
            WHERE id NOT IN ({placeholders});
        ''', list(ids_to_keep))
        conn.commit()

    start_time = time.time()
    cursor.execute('VACUUM')
    conn.commit()
    end_time = time.time()
    elapsed_time = end_time - start_time
    return elapsed_time

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

record_counts = []

search_key_times = []
search_non_key_times = []
search_mask_times = []
add_time = []
add_group_time = []
update_key_time = []
update_non_key_time = []
delete_key_time = []
delete_non_key_time = []
delete_group_time = []
vacuum_time = []
compress_time = []

for n in range(3):
    cursor.execute('DELETE FROM test')
    conn.commit()
    
    cursor.execute('VACUUM')
    conn.commit()
    print(f"Записей: {10**(n+3):,}")
    record_counts.append(10**(n+3))
    for i in range(10**(n+3)):
        unique_text = f"unique_text-{i}"
        not_unique_text = f"not_unique_text-{i%(200 * 10**n)}"
        cursor.execute('''
        INSERT INTO test (unique_text, not_unique_text) VALUES (?, ?);
        ''', (unique_text, not_unique_text))
    conn.commit()

    _, elapsed_time = find_record_by_id(100 * 10**n)

    _, elapsed_time = find_record_by_id(500 * 10**n)
    search_key_times.append(10**6*elapsed_time)
    print(f'Поиск по ключевому полю: {10**6*elapsed_time:.2f} μs')

    _, elapsed_time = find_record_by_unique_text(f"unique_text-{500 * 10**n}")
    search_non_key_times.append(10**6*elapsed_time)
    print(f'Поиск по не ключевому полю: {10**6*elapsed_time:.2f} μs')

    _, elapsed_time = find_record_by_mask(f"not_unique_text-%{100 * 10**n}%")
    search_mask_times.append(10**6*elapsed_time)
    print(f'Поиск по маске: {10**6*elapsed_time:.2f} μs')

    elapsed_time = add_record(f"unique_text-{10**(n+3)+1}", f"not_unique_text-{1}")
    add_time.append(10**6*elapsed_time)
    print(f"Запись добавлена за: {10**6*elapsed_time:.2f} μs")

    records_to_add = []
    for i in range(100): 
        unique_text = f"unique_text-{10**(n+3)+2+i}"
        not_unique_text = f"not_unique_text-{1}"
        records_to_add.append((unique_text, not_unique_text))

    elapsed_time = add_records(records_to_add)
    add_group_time.append(10**6*elapsed_time)
    print(f"Группа записей(100) добавлена за: {10**6*elapsed_time:.2f} μs")

    elapsed_time = update_record(10**(n+3)+1, f"unique_text-{10**(n+3)+1}11", f"not_unique_text-{100}")

    elapsed_time = update_record(10**(n+3)+1, f"unique_text-{10**(n+3)+1}'", f"not_unique_text-{10}")
    update_key_time.append(10**6*elapsed_time)
    print(f"Изменение записи (определение по ключевому полю) : {10**6*elapsed_time:.2f} μs")

    elapsed_time = update_record_by_unique_text(f"unique_text-{10**(n+3)+1}'", f"not_unique_text-{100}")
    update_non_key_time.append(10**6*elapsed_time)
    print(f"Изменение записи (определение по не ключевому полю) : {10**6*elapsed_time:.2f} μs")

    elapsed_time = delete_record_by_id(500 * 10**n)
    delete_key_time.append(10**6*elapsed_time)
    print(f"Удаление записи (определение по ключевому полю)  : {10**6*elapsed_time:.2f} μs")

    elapsed_time = delete_record_by_unique_text(f"unique_text-{10**(n+3)+1}'")
    delete_non_key_time.append(10**6*elapsed_time)
    print(f"Удаление записи (определение по не ключевому полю): {10**6*elapsed_time:.2f} μs")

    elapsed_time = delete_records_by_id([i for i in range(100 * 10**n, 100 * 10**n+100)])
    delete_group_time.append(10**6*elapsed_time)
    print(f"Удаление группы записей  (определение по ключевому полю, 100): {10**6*elapsed_time:.2f} μs")

    cursor.execute('VACUUM')
    conn.commit()

    elapsed_time = vacuum_delete_records_by_id([i for i in range(100 * 10**n + 200, 100 * 10**n+200+100)])
    vacuum_time.append(10**6*elapsed_time)
    print(f"Cжатие базы данных (после удаления из БД 100 строк) : {10**6*elapsed_time:.2f} μs")

    elapsed_time = delete_all_except_last_n(100)
    compress_time.append(10**6*elapsed_time)
    print(f"Сжатие базы данных (после удаления, всех, кроме 100 строк) : {10**6*elapsed_time:.2f} μs")


conn.commit()
cursor.close()
conn.close()


fig, axs = plt.subplots(2, 2, figsize=(12, 10))

# Группа 1: Поиск
axs[0, 0].plot(record_counts, search_key_times, label='Поиск по ключевому полю')
axs[0, 0].plot(record_counts, search_non_key_times, label='Поиск по не ключевому полю')
axs[0, 0].plot(record_counts, search_mask_times, label='Поиск по маске')
axs[0, 0].set_title('Поиск')
axs[0, 0].set_xlabel('Число записей')
axs[0, 0].set_ylabel('Время, μs')
axs[0, 0].set_xscale('log')
axs[0, 0].set_yscale('log')
axs[0, 0].legend()
axs[0, 0].grid(True)

# Группа 2: Добавление и изменение
axs[0, 1].plot(record_counts, add_time, label='Добавление записи')
axs[0, 1].plot(record_counts, add_group_time, label='Добавление группы записей (100)')
axs[0, 1].plot(record_counts, update_key_time, label='Изменение записи (по ключевому полю)')
axs[0, 1].plot(record_counts, update_non_key_time, label='Изменение записи (по не ключевому полю)')
axs[0, 1].set_title('Добавление и Изменение')
axs[0, 1].set_xlabel('Число записей')
axs[0, 1].set_ylabel('Время, μs')
axs[0, 1].set_xscale('log')
axs[0, 1].set_yscale('log')
axs[0, 1].legend()
axs[0, 1].grid(True)

# Группа 3: Удаление
axs[1, 0].plot(record_counts, delete_key_time, label='Удаление записи (по ключевому полю)')
axs[1, 0].plot(record_counts, delete_non_key_time, label='Удаление записи (по не ключевому полю)')
axs[1, 0].plot(record_counts, delete_group_time, label='Удаление группы записей (по ключевому полю)')
axs[1, 0].set_title('Удаление')
axs[1, 0].set_xlabel('Число записей')
axs[1, 0].set_ylabel('Время, μs')
axs[1, 0].set_xscale('log')
axs[1, 0].set_yscale('log')
axs[1, 0].legend()
axs[1, 0].grid(True)

# Группа 4: Сжатие базы данных
axs[1, 1].plot(record_counts, vacuum_time, label='Сжатие БД (после удаления 200 строк)')
axs[1, 1].plot(record_counts, compress_time, label='Сжатие БД (после удаления всех, кроме 200 строк)')
axs[1, 1].set_title('Сжатие базы данных')
axs[1, 1].set_xlabel('Число записей')
axs[1, 1].set_ylabel('Время, μs')
axs[1, 1].set_xscale('log')
axs[1, 1].set_yscale('log')
axs[1, 1].legend()
axs[1, 1].grid(True)

# Отображение графиков
plt.tight_layout()
plt.show()


def format_data(*extra_arrays):
    max_len = max(map(len, extra_arrays))
    for i in range(max_len):
        for array in extra_arrays:
            if i < len(array):
                parts = "{:.1e}".format(array[i]).split("e")
                formatted = f"{float(parts[0]):.1f} \\cdot 10^{{{int(parts[1])}}}"
                print(f"${formatted}$", end=" & ") 
                print("", end=" ")
        print("\\\\") 




format_data(record_counts, search_key_times, search_non_key_times, search_mask_times, add_time, add_group_time, update_key_time, update_non_key_time, delete_key_time, delete_non_key_time, delete_group_time, vacuum_time, compress_time)




# plt.plot(record_counts, search_key_times, label='Поиск по ключевому полю')
# plt.plot(record_counts, search_non_key_times, label='Поиск по не ключевому полю')
# plt.plot(record_counts, search_mask_times, label='Поиск по маске')
# plt.plot(record_counts, add_time, label='Добавление записи')
# plt.plot(record_counts, add_group_time, label='Добавление группы записей(100)')
# plt.plot(record_counts, update_key_time, label='Изменение записи (определение по ключевому полю)')
# plt.plot(record_counts, update_non_key_time, label='Изменение записи (определение по не ключевому полю)')
# plt.plot(record_counts, delete_key_time, label='Удаление записи (определение по ключевому полю)')
# plt.plot(record_counts, delete_non_key_time, label='Удаление записи (определение по не ключевому полю) ')
# plt.plot(record_counts, delete_group_time, label='Удаление группы записей (определение по ключевому полю)')
# plt.plot(record_counts, vacuum_time, label='Сжатие базы данных (после удаления из БД 200 строк) ')
# plt.plot(record_counts, compress_time, label='Сжатие базы данных (после удаления, всех, кроме 200 строк)')
# plt.xscale('log')
# plt.yscale('log')

# # plt.title("")
# plt.xlabel('Число записей ')
# plt.ylabel('Время, μs')
# plt.legend()
# plt.grid(True)

# plt.show()