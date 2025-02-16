from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest
import time


@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    driver.get("http://tech-avito-intern.jumpingcrab.com/")

    # Ожидание полной загрузки страницы
    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    yield driver
    driver.quit()


def test_create_ad(driver):
    try:
        # Ожидание и клик по кнопке создания
        create_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/create') and contains(text(), 'Добавить')]"))
        )
        create_btn.click()

        # Заполнение формы
        title_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='title']"))
        )
        title_field.send_keys("Тестовый товар")

        price_field = driver.find_element(By.CSS_SELECTOR, "input[name='price']")
        price_field.send_keys("1000")

        submit_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Сохранить')]"))
        )
        submit_btn.click()

        # Проверка создания
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Тестовый товар')]"))
        )

    except Exception as e:
        driver.save_screenshot("create_ad_error.png")
        raise e


def test_edit_ad(driver):
    try:
        # Поиск элемента для редактирования
        edit_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH,
                                        "//h2[contains(., 'Тестовый товар')]/ancestor::div[@class='ad-item']//a[contains(@href, 'edit')]"))
        )
        edit_link.click()

        # Редактирование цены
        price_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='price']"))
        )
        price_field.clear()
        price_field.send_keys("1500")

        # Сохранение изменений
        driver.find_element(By.XPATH, "//button[contains(text(), 'Обновить')]").click()

        # Проверка обновления
        WebDriverWait(driver, 20).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//h2[contains(., 'Тестовый товар')]/ancestor::div[@class='ad-item']//div[@class='price']"),
                "1500"
            )
        )

    except Exception as e:
        driver.save_screenshot("edit_ad_error.png")
        raise e


def test_search_ads(driver):
    try:
        # Поиск и фильтрация
        search_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Поиск объявлений']"))
        )
        search_field.send_keys("Тестовый")

        # Сортировка
        driver.find_element(By.CSS_SELECTOR, "select[name='sort']").click()
        driver.find_element(By.XPATH, "//option[contains(text(), 'убыванию цены')]").click()

        # Пагинация
        driver.find_element(By.CSS_SELECTOR, "select[name='per_page']").click()
        driver.find_element(By.XPATH, "//option[contains(text(), '10')]").click()

        # Ожидание обновления списка
        time.sleep(2)  # Для стабильности AJAX-запроса

        # Проверка результатов
        items = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ad-list > div.ad-item"))
        )
        assert len(items) <= 10, "Количество элементов превышает 10"
        assert any("Тестовый" in item.text for item in items), "Не найдены тестовые объявления"

    except Exception as e:
        driver.save_screenshot("search_ads_error.png")
        raise e


def test_view_ad_details(driver):
    try:
        # Переход в детали
        ad_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//h2[contains(., 'Тестовый товар')]"))
        )
        ad_link.click()

        # Проверка деталей
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Тестовый товар')]"))
        )
        WebDriverWait(driver, 20).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".price"), "1500")
        )

        # Возврат на главную
        driver.back()

    except Exception as e:
        driver.save_screenshot("view_details_error.png")
        raise e
