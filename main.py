"""Точка запуска системы учёта коммерческих предложений."""

from datetime import date
from pathlib import Path

from proposals import (
    STATUS_APPROVED,
    STATUS_CANCELLED,
    STATUS_PENDING,
    Proposal,
    add_proposal,
    calculate_expiration_date,
    calculate_final_amount,
    calculate_statistics,
    change_proposal_status,
    find_proposals,
    iter_proposals_by_status,
    sort_proposals_by_amount,
)
from storage import load_proposals, save_proposals
from utils import input_date, input_float, input_int, input_non_empty

DATA_FILE = str(Path(__file__).parent / "data" / "proposals.json")


def show_proposals(proposals: list[Proposal]) -> None:
    """Вывести коммерческие предложения в читаемом виде."""
    if not proposals:
        print("Коммерческие предложения не найдены.")
        return

    for proposal in proposals:
        created_date = date.fromisoformat(str(proposal["created_date"]))
        expiration_date = calculate_expiration_date(
            created_date,
            int(proposal["validity_days"]),
        )
        final_amount = calculate_final_amount(
            float(proposal["amount"]),
            float(proposal["discount_percent"]),
        )
        print(
            f'{proposal["id"]}. {proposal["number"]} | '
            f'{proposal["client"]} | '
            f"{final_amount:.2f} руб. | "
            f"до {expiration_date:%d.%m.%Y} | "
            f'{proposal["status"]}'
        )


def show_statistics(proposals: list[Proposal]) -> None:
    """Вывести сводную статистику по предложениям."""
    statistics = calculate_statistics(proposals)
    print(f'Всего предложений: {statistics["total_count"]}')
    print(f'Активных предложений: {statistics["active_count"]}')
    print(f'Согласованных предложений: {statistics["approved_count"]}')
    print(f'Уникальных клиентов: {statistics["unique_clients_count"]}')
    print(f'Общая итоговая сумма: {statistics["total_amount"]:.2f} руб.')
    print(
        "Средняя итоговая сумма: "
        f'{statistics["average_amount"]:.2f} руб.'
    )


def create_proposal_from_input(
    proposals: list[Proposal],
) -> Proposal:
    """Запросить данные и создать коммерческое предложение."""
    proposal_number = input_non_empty("Номер предложения: ")
    client_name = input_non_empty("Название клиента: ")
    amount = input_float("Исходная сумма: ")
    discount_percent = input_float("Скидка, %: ")
    created_date = input_date("Дата создания (ДД.ММ.ГГГГ): ")
    validity_days = input_int("Срок действия в днях: ")
    return add_proposal(
        proposals,
        proposal_number,
        client_name,
        amount,
        discount_percent,
        created_date,
        validity_days,
    )


def print_menu() -> None:
    """Вывести главное меню приложения."""
    print("\n=== Система учёта коммерческих предложений ===")
    print("1. Показать все предложения")
    print("2. Найти предложение")
    print("3. Добавить предложение")
    print("4. Согласовать предложение")
    print("5. Отменить предложение")
    print("6. Отсортировать по итоговой сумме")
    print("7. Отобрать предложения по статусу")
    print("8. Показать статистику")
    print("0. Выход")


def select_status() -> str:
    """Запросить у пользователя один из доступных статусов."""
    statuses = {
        1: STATUS_PENDING,
        2: STATUS_APPROVED,
        3: STATUS_CANCELLED,
    }
    print("1. Ожидает согласования")
    print("2. Согласовано")
    print("3. Отменено")
    status_number = input_int("Выберите статус: ")
    if status_number not in statuses:
        raise ValueError("Неизвестный номер статуса")
    return statuses[status_number]


def main() -> None:
    """Загрузить данные и запустить цикл меню приложения."""
    try:
        proposals = load_proposals(DATA_FILE)
    except ValueError as error:
        print(f"Ошибка загрузки: {error}")
        proposals = []

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                show_proposals(proposals)
            elif choice == "2":
                query = input_non_empty("Номер или клиент: ")
                show_proposals(find_proposals(proposals, query))
            elif choice == "3":
                proposal = create_proposal_from_input(proposals)
                save_proposals(DATA_FILE, proposals)
                print(f'Предложение {proposal["number"]} добавлено.')
            elif choice == "4":
                proposal_id = input_int("ID предложения: ")
                change_proposal_status(
                    proposals,
                    proposal_id,
                    STATUS_APPROVED,
                )
                save_proposals(DATA_FILE, proposals)
                print("Предложение согласовано.")
            elif choice == "5":
                proposal_id = input_int("ID предложения: ")
                change_proposal_status(
                    proposals,
                    proposal_id,
                    STATUS_CANCELLED,
                )
                save_proposals(DATA_FILE, proposals)
                print("Предложение отменено.")
            elif choice == "6":
                sorted_proposals = sort_proposals_by_amount(
                    proposals,
                    reverse=True,
                )
                show_proposals(sorted_proposals)
            elif choice == "7":
                selected_status = select_status()
                filtered = list(
                    iter_proposals_by_status(
                        proposals,
                        selected_status,
                    )
                )
                show_proposals(filtered)
            elif choice == "8":
                show_statistics(proposals)
            elif choice == "0":
                save_proposals(DATA_FILE, proposals)
                print("Данные сохранены. Работа завершена.")
                break
            else:
                print("Неизвестная команда. Повторите ввод.")
        except ValueError as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
