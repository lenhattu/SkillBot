import webdriver
import os
import time
import json
import csv
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import skill_static_analysis
import nlp_tools
from timeout_decorator import *

#import stanza
#stanza.download('en')
#nlp_engine = stanza.Pipeline(lang='en', processors='tokenize,pos')


# path_experiment = 'C:/Users/tule/GoogleDriveUVA/experiments/updateJune2020/'

path_html = '/media/sf_dataset2020/sample_html_set/set0/'
path_results = '/media/sf_SkillBotEvaluation/sample_v2/set0/'


def parse_directive(driver):
    time.sleep(1)
    content = driver.find_element(By.XPATH, '//*[@id="brace-editor"]/div[2]/div/div[3]')
    directive = json.loads(nlp_tools.remove_html_tags(content.get_attribute('innerHTML')))
    return directive


def get_response(driver, utterance, num_responses_prev):
    #if driver.find_elements(By.XPATH, '//*[@id="astro-tabs-1-panel-0"]/div[1]/div[2]/input').isEmpty():
    #    driver.refresh()
    #driver.find_element(By.XPATH, '//*[@id="root"]/div/div/section[1]/div[2]/fieldset/div/label[3]/i').click()

    field_utterance = driver.find_element(By.XPATH, '//*[@id="astro-tabs-1-panel-0"]/div[1]/div[2]/input')
    field_utterance.send_keys(utterance)
    field_utterance.send_keys(Keys.ENTER)
    time.sleep(4)

    # wait for all responses
    #wait_for_response = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "askt-dialog__message askt-dialog__message--active-response")))
    list_directives = list()

    giveup = time.time() + 3
    while len(list_directives) <= num_responses_prev:
        if time.time() > giveup:
            return ([], len(list_directives))
        list_directives = driver.find_elements(By.XPATH, "//span[contains(text(),'Directive: SpeechSynthesizer')]")
    #list_play = driver.find_elements(By.XPATH, "//span[contains(text(),'SpeechSynthesizer.Play')]")
    #time.sleep(2)

    list_responses = list()
    for item in list_directives:
        #item.click()
        driver.execute_script("arguments[0].click();", item)
        directive = parse_directive(driver)
        list_responses.append(directive["payload"]["caption"].strip())
    return (list_responses[num_responses_prev:], len(list_responses))

    #html = driver.find_element_by_xpath("//html").get_attribute('outerHTML')
    #with open('conversation.html', 'w', encoding='utf-8') as file_skill:
    #    file_skill.write(html)


def concat_responses(list_responses):
    response_final = ""
    for item in list_responses:
        response_final += item + ". "
    return response_final


def is_used_cmd(skill, resp, cmd):
    path_file = path_results + skill + '.json'
    if os.path.isfile(path_file) and os.access(path_file, os.R_OK):
        # load current data
        with open(path_file, 'r', encoding='utf-8') as json_in:
            data = json.load(json_in)

        # check if the cmd was already used
        for conversation in data:
            if resp in conversation:
                cmd_idx = conversation.index(resp) - 1
                if cmd == conversation[cmd_idx]:
                    return True
    return False


def update_database(skill, conversation):
    path_file = path_results + skill + '.json'
    if os.path.isfile(path_file) and os.access(path_file, os.R_OK):
        # load current data
        with open(path_file, 'r', encoding='utf-8') as json_in:
            data = json.load(json_in)
        # check duplicate
        if conversation in data:
            return False
        # update data and save
        data.append(conversation)
        with open(path_file, 'w', encoding='utf-8') as json_out:
            json.dump(data, json_out, ensure_ascii=False, indent=4)
        return True
    else:
        # if new
        data = list()
        data.append(conversation)
        with open(path_file, 'w', encoding='utf-8') as json_out:
            json.dump(data, json_out, ensure_ascii=False, indent=4)
        return True


@timeout(360)
def interact_with_skill(filename, driver):
    skill = filename[:-5]
    # get the skill's sample utterances
    list_utterances_opening = list()
    list_utterances_inskill = list()
    list_utterances = skill_static_analysis.get_all_sample_utterances(path_html + filename)
    list_utterances.extend(skill_static_analysis.get_additional_utterances_from_description(path_html + filename))
    for utterance in list_utterances:
        if skill_static_analysis.is_opening_utterance(path_html + filename, utterance):
            list_utterances_opening.append(utterance)
        else:
            list_utterances_inskill.append(utterance)

    time.sleep(2)

    # test each utterance
    for utterance in list_utterances:
        conversation = list()
        wait = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div/div/div/div[3]/div/div/section[1]/div[2]/fieldset/div/label[3]')))
        ele = driver.find_element(By.XPATH,
                                  '/html/body/div[1]/div/div/div/div/div[3]/div/div/section[1]/div[2]/fieldset/div/label[3]')
        driver.execute_script("arguments[0].click();", ele)
        num_responses_prev = 0

        if utterance in list_utterances_inskill:
            if len(list_utterances_opening) > 0:
                init_utterance = list_utterances_opening[0]
            else:
                init_utterance = skill_static_analysis.create_custom_opening_utterance(path_html + filename)
            list_responses, num_responses_prev = get_response(driver, init_utterance, num_responses_prev)
            conversation.append(init_utterance)
            conversation.append(concat_responses(list_responses))
            # num_responses_prev = len(list_responses)

        list_responses, num_responses_prev = get_response(driver, utterance, num_responses_prev)
        conversation.append(utterance)
        conversation.append(concat_responses(list_responses))
        # num_responses_prev = len(list_responses)

        # subsequent rounds after starting the skill
        whole_response = concat_responses(list_responses)
        list_seen_sentence = list()
        stop = False
        while True:
            if stop:
                break
            quiz_answers = nlp_tools.generate_answer_quiz(whole_response)
            if quiz_answers:
                cmd = random.choice(quiz_answers)
                for ans in quiz_answers:
                    if not is_used_cmd(skill, whole_response, ans):
                        cmd = ans
                        break
            else:
                result = nlp_tools.identify_question_in_paragraph(whole_response)
                sentence = result[0]
                restype = result[1]
                if sentence in list_seen_sentence:
                    stop = True
                else:
                    list_seen_sentence.append(sentence)
                if restype == "yn":
                    yn_answers = nlp_tools.generate_answer_yn()
                    cmd = random.choice(yn_answers)
                    for ans in yn_answers:
                        if not is_used_cmd(skill, whole_response, ans):
                            cmd = ans
                            break
                elif restype == "wh":
                    wh_answers = nlp_tools.generate_answer_wh(sentence, result[2])
                    if len(wh_answers) > 1:
                        cmd = random.choice(wh_answers)
                        for ans in wh_answers:
                            if not is_used_cmd(skill, whole_response, ans):
                                cmd = ans
                                break
                    else:
                        cmd = wh_answers[0]
                else:
                    o_answers = nlp_tools.generate_answer_other(sentence)
                    if len(o_answers) > 1:
                        cmd = random.choice(o_answers)
                        for ans in o_answers:
                            if not is_used_cmd(skill, whole_response, ans):
                                cmd = ans
                                break
                    else:
                        cmd = o_answers[0]

            list_responses, num_responses_prev = get_response(driver, cmd, num_responses_prev)
            whole_response = concat_responses(list_responses)
            print("CMD: ", cmd)
            print("Whole: ", whole_response)
            if whole_response in conversation or "I don't know that" in whole_response or "I'm not sure" in whole_response or "I’m not sure" in whole_response or whole_response == "":
                stop = True
            else:
                conversation.append(cmd)
                conversation.append(whole_response)
                # num_responses_prev = len(list_responses)
        if (len(conversation) == 2) and ("I don't know that" in conversation[1] or "I'm not sure" in conversation[1] or "I’m not sure" in conversation[1] or conversation[1] == ""):
            pass
        else:
            update_database(skill, conversation)
        driver.refresh()


def scrape_skills():
    # disable all skills
    # disable_skills.disable_all_skills()

    # get progress: completed skills
    list_completed = list()
    with open('progress0.csv', 'r') as file_progress_in:
        reader = csv.reader(file_progress_in)
        for row in reader:
            list_completed.append(row[0])
    #list_completed = list()
    #for file_result in os.listdir(path_results):
    #    if '.json' in file_result:
    #        list_completed.append(file_result[:-5])
    print('Number of completed skills: ', len(list_completed))

    # ignored list
    # list_ignored = ['B07H88P868', 'B07BVW7WTF', 'B07C8RFDLD', 'B074G4YL1X', 'B07NPC1W56', 'B07VDP7ZYQ', 'B07TD89P9G',
    #                'B01N0EJ7ET', 'B07KNLC1HD', 'B078W199Z3']
    list_ignored = ['B01N0EZKL0',  'B07QFVC5BF', 'B07K5C96NG', 'B07JKY7G94', 'B075PLL36H', 'B07573DPKD', 'B07572QHMB', 'B074PHT2CP', 'B0746BQHK5', 'B0735YC12V', 'B0721H76RB', 'B0716LCY24', 'B01CF059GM', 'B071HDNM4S', 'B07CRRC39X', 'B07WSR7J9B', 'B07PQBDFTW', 'B07PRG69YP', 'B07RNJPGYC', 'B07VRBL9D1', 'B07X8QX92D', 'B07K9ZYVYX', 'B07KNLC1HD']
    # list_ignored = ['B074PHT2CP', 'B01N0EJ7ET', 'B07KNLC1HD']
    # list_ignored = []

    # test each skill
    for filename in os.listdir(path_html):
        skill = filename[:-5]
        if (skill in list_completed) or (skill in list_ignored):
            continue
        print('Testing: ', skill)

        driver = webdriver.get_firefox()
        driver.get('https://developer.amazon.com/alexa/console/ask/test/amzn1.ask.skill.29ba1e43-78ab-435e-a548-78ef65b4ba77/development/en_US/')

        try:
            interact_with_skill(filename, driver)
            with open('progress0.csv', 'a') as file_progress_out:
                writer = csv.writer(file_progress_out, lineterminator='\n')
                writer.writerow([skill])
        except TimeoutError:
            driver.close()
            driver.quit()
            continue

        # close driver
        driver.close()
        driver.quit()


if __name__ == '__main__':
    #if not os.path.exists(path_results):
    #    os.mkdir(path_results)
    start = time.time()
    scrape_skills()
    #while True:
    #    try:
    #        scrape_skills()
    #        break
    #    except:
    #        continue
    end = time.time()
    time_exec = end - start
    print('Total exec time: ', time_exec/3600)
