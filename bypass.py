import asyncio
from pyppeteer import launch
from capsolver_api import HCaptchaTask
import os

async def save_text_as_txt(file_path, content):
    # os.makedirs(os.path.dirname("save_datas"), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

async def main():
    url = 'https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp'
    browser = await launch(headless=False)
    page = await browser.newPage()
    await page.goto(url)
    element = await page.querySelector('#hcaptcha')
    website_key = await page.evaluate('(element) => element.getAttribute("data-sitekey")', element)
    capsolver = HCaptchaTask('CAP-2A629AC8B2D76F4E628422EFF87A95D6')
    task_id = capsolver.create_task(task_type='HCaptchaTaskProxyLess',
                                    website_url=url,
                                    website_key=website_key,
                                    is_invisible=True
                                    )
    while True:
        solution = capsolver.get_solution(task_id)
        if solution:
            captcha_key = solution["gRecaptchaResponse"]
            break
        await asyncio.sleep(2)
    txt_cpf_element = await page.querySelector('input[name="txtCPF"]')
    if txt_cpf_element:
        await txt_cpf_element.type("06780432627")
    else:
        print("txtCPF element not found!")
    txt_data_nascimento_element = await page.querySelector('input[name="txtDataNascimento"]')
    if txt_data_nascimento_element:
        await txt_data_nascimento_element.type("20/05/1983")
    else:
        print("txtDataNascimento element not found!")
    await page.waitForSelector('iframe')
    await page.evaluate('(element, captchaKey) => element.value = captchaKey',
                        await page.querySelector('textarea[name="h-captcha-response"]'),
                        captcha_key)
    await page.waitFor(2000)
    btn = await page.querySelector('input[name="Enviar"]')
    await btn.click()
    await page.waitFor(5000)
    titleSelector = "h1[class='documentFirstHeading']"
    title = await page.evaluate('(selector) => document.querySelector(selector).textContent', titleSelector)
    print(title)
    selector = "h4"
    text = await page.evaluate('(selector) => document.querySelector(selector).textContent', selector)
    file_path = "06780432627" + ".txt"
    savedTxt = title + "\n" + text
    await save_text_as_txt(file_path, savedTxt)
    print(text)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())