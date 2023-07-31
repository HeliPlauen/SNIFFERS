<?php
/* 
// Отправка портов по запросу
action = ports
data = session_key
resp = json

// Получение game_name
action = get_game_name
data = session_key
resp = "name"

// Получить статус компьютера
action = get_comp_status
data = computer_id
resp = "status"

// Изменить статус компьютера с на busy
action = set_comp_busy
data = session_key
resp = 0

// Изменить статус компьютера с на ready
action = set_comp_ready
data = computer_id
resp = 0

// Проверка существования сессии
action = session_exists_check
data = session_key
resp = 0 (если нет сессиии)
resp = 1 (если есть сессия)
!!!!!!!!!!!!!! (потом заменю наоборот)

// Обновление времени сессии
action = update_session_time
data = session_key
resp = 0 (обновилось)
resp = 1 (сессии нет)

// Освободить компьютер (изменить статус на ready и удалить сессию)
action = free_computer
data = session_key
resp = 0 
*/

/**
 * connect_db
 */
/* function connect_db()
{
    global $wpdb;
    $wpdb = new wpdb(DB_USER, DB_PASSWORD, DB_NAME, DB_HOST);
    if (!empty($wpdb->error))
        wp_die($wpdb->error);
    return $wpdb;
} */


/* 
* Компьютеры
*/
// Отправка портов по запросу
add_action('wp_ajax_ports', 'ports');
add_action('wp_ajax_nopriv_ports', 'ports');
function ports()
{
    global $wpdb;

    $session_key = trim($_POST['session_key']);
    $computer_id = $wpdb->get_results("SELECT `computer_id`, `game_id` FROM `sessions` WHERE `session_key` = '" . $session_key . "' ");
    $comp_ready = $wpdb->get_results("SELECT `id`, `local_ip`, `global_ip`, `TCP_ports`,`UDP_ports` FROM `computers_information` WHERE `id` = '" . $computer_id[0]->computer_id . "' ");
    $game_name = $wpdb->get_results("SELECT `meta_value` FROM `wp_postmeta` WHERE `post_id` = '" . $computer_id[0]->game_id . "' AND `meta_key` = 'game_real_name' ");

    $resp = 0;
    if (count($comp_ready) != 0) {
        $comp_ready[0]->game_name = $game_name[0]->meta_value;
        $resp = json_encode($comp_ready[0]);
    }

    message_to_telegram("КОМП'ЮТЕР\nОтримані порти у " . $computer_id[0]->computer_id);

    echo $resp;
    wp_die();
}

// Получение game_name
add_action('wp_ajax_get_game_name', 'get_game_name');
add_action('wp_ajax_nopriv_get_game_name', 'get_game_name');
function get_game_name()
{
    global $wpdb;
    $session_key = trim($_POST['session_key']);
    $game_id = $wpdb->get_results("SELECT `game_id`, `launcher` FROM `sessions` WHERE `session_key` = '" . $session_key . "'");
    $real_game_name = $wpdb->get_results("SELECT `meta_value` FROM `wp_postmeta` WHERE `post_id` = '" . $game_id[0]->game_id . "' AND `meta_key` = 'game_real_name' ");
    $real_game_name = $real_game_name[0]->meta_value;
    $game_name = $wpdb->get_results("SELECT `post_title` FROM `wp_posts` WHERE `ID` = '" . $game_id[0]->game_id . "'");

    if ($game_id[0]->launcher != 'none' && $game_id[0]->launcher != '')
        $real_game_name .= ('_' . $game_id[0]->launcher);

    /* $names = array(
        'name' => $game_name[0]->post_title,
        'real_name' => $real_game_name
    );
    echo json_encode($names); */
    // message_to_telegram(" $game_name[0]->post_title . "===" . $real_game_name");
    message_to_telegram("КОМП'ЮТЕР\nОтримано ім'я гри " . $game_name[0]->post_title . "===" . $real_game_name . " у " . $session_key);

    echo $game_name[0]->post_title . "===" . $real_game_name; //$game_name[0]->post_title . "===" .
    wp_die();
}

// Получить статус компьютера
add_action('wp_ajax_get_comp_status', 'get_comp_status');
add_action('wp_ajax_nopriv_get_comp_status', 'get_comp_status');
function get_comp_status()
{
    global $wpdb;
    $computer_id = trim($_POST['computer_id']);
    $resp = $wpdb->get_results("SELECT `status` FROM `computers_information` WHERE `id` = '" . $computer_id . "' ");

    // message_to_telegram("КОМПЬЮТЕР\nПолучен статус компьютера " . $computer_id);

    echo $resp[0]->status;
    wp_die();
}

// Смена компа если не работает
add_action('wp_ajax_choose_another_comp', 'choose_another_comp');
add_action('wp_ajax_nopriv_choose_another_comp', 'choose_another_comp');
function choose_another_comp()
{
    $response = [];
    if (isset($_POST['session_key'])) {
        $session_key = trim($_POST['session_key']);

        global $wpdb;
        $computer_id = $wpdb->get_results($wpdb->prepare(
            "SELECT `id` FROM `computers_information` WHERE `status` = 'ready' AND `state` = 'online'"
        ));
        if (count($computer_id) > 0) {
            $new_id = random_int(0, count($computer_id) - 1);
            $old_computer_id = $wpdb->get_results($wpdb->prepare("SELECT `computer_id` FROM `sessions` WHERE `session_key` = '$session_key'"));
while ($new_id == $old_computer_id) {
                $new_id = random_int(0, count($computer_id) - 1);
            }
            $answ = $wpdb->update('sessions', ['computer_id' => $computer_id[$new_id]->id], ['session_key' => $session_key]);
            if ($answ == 1) {
                $wpdb->update('computers_information', ['status' => 'cleaning'], ['id' => $old_computer_id[0]->computer_id]);
                $wpdb->update('computers_information', ['status' => 'waiting'], ['id' => $computer_id[$new_id]->id]);
                message_to_telegram("КОМП'ЮТЕР\nКомп'ютер сесії $session_key змінений з " . $old_computer_id[0]->computer_id . " на " . $computer_id[$new_id]->id);
                message_to_telegram("КОМП'ЮТЕР\nКомп'ютер сесії $session_key змінений з " . $old_computer_id[0]->computer_id . " на " . $computer_id[$new_id]->id, '5342616919:AAEmPzUunROmHzf8HHnJNRNg9X6zrAHX-EI');
            } else
                $response['error'] = 'Помилка зміни компʼютера';
        } else
            $response['error'] = 'Немає вільних компʼютерів';
    } else
        $response['error'] = 'Надіслано неправильні дані';

    // $response['status'] = array_key_exists('error', $response) == false;
    if (array_key_exists('error', $response) == false)
        echo 0;
    else
        echo json_encode($response);

    // echo json_encode($response);
    wp_die();
}

// Изменить статус компьютера с на busy
// 1 не верный параметр
// 2 нет такой сессии
add_action('wp_ajax_set_comp_busy', 'set_comp_busy');
add_action('wp_ajax_nopriv_set_comp_busy', 'set_comp_busy');
function set_comp_busy()
{
    global $wpdb;
    if (isset($_POST['session_key'])) {
        $session_key = trim($_POST['session_key']);
        $computer_id = $wpdb->get_results($wpdb->prepare(
            "SELECT `computer_id` FROM `sessions` WHERE `session_key` = '" . $session_key . "' "
        ));
        if (count($computer_id) > 0) {
            $wpdb->get_results($wpdb->prepare(
                "UPDATE `computers_information` SET `status` = 'busy' WHERE `computers_information`.`id` = '" . $computer_id[0]->computer_id . "'"
            ));

            message_to_telegram("КОМП'ЮТЕР\nСтатус комп'ютера змінено на busy на " . $computer_id[0]->computer_id . " пк");

            echo 0;
        } else {
            message_to_telegram("КОМП'ЮТЕР\nПомилка зміни статусу на busy, сесія не існує");
            message_to_telegram("КОМП'ЮТЕР\nПомилка зміни статусу на busy, сесія не існує", '5342616919:AAEmPzUunROmHzf8HHnJNRNg9X6zrAHX-EI');
            echo 2;
        }
    } else {
        message_to_telegram("КОМП'ЮТЕР\nПомилка зміни статусу на busy, не вірні дані");
        // message_to_telegram("КОМПЬЮТЕР\nОшибка изменения статуса на busy, не верные данные", '5342616919:AAEmPzUunROmHzf8HHnJNRNg9X6zrAHX-EI');
        echo 1;
    }
    wp_die();
}

// Изменить статус компьютера с на ready
add_action('wp_ajax_set_comp_ready', 'set_comp_ready');
add_action('wp_ajax_nopriv_set_comp_ready', 'set_comp_ready');
function set_comp_ready()
{
    global $wpdb;
    $computer_id = trim($_POST['computer_id']);
    $session = $wpdb->get_results("SELECT * FROM `sessions` WHERE `computer_id` = '" . $computer_id . "'");
    if (count($session) != 0) {
        $wpdb->get_results("UPDATE `computers_information` SET `errore_code` = '1' WHERE `id` = '" . $computer_id . "'");
        $wpdb->get_results("DELETE FROM sessions WHERE `sessions`.`computer_id` = '" . $computer_id . "'");
    }
    $wpdb->get_results("UPDATE `computers_information` SET `status` = 'ready' WHERE `computers_information`.`id` = '" . $computer_id . "'");

    message_to_telegram("КОМП'ЮТЕР\nСтатус комп'ютера змінено на ready на " . $computer_id . " пк");
    message_to_telegram("КОМП'ЮТЕР\nСтатус комп'ютера змінено на ready на " . $computer_id . " пк", '5342616919:AAEmPzUunROmHzf8HHnJNRNg9X6zrAHX-EI');

    echo 0;
    wp_die();
}



/* 
* Сессии
*/
// Создание сессии
/* 
* 1 не зареган
* 2 недостаточно часов
* 3 нет свободных компьютеров
* 4 Не корректный id компьютера 
* 5 Выбранный компьютер занят
* 6 Нельзя сменить компьютер. Завершите старую сессию
 */
add_action('wp_ajax_session_create', 'session_create');
add_action('wp_ajax_nopriv_session_create', 'session_create');
function session_create()
{
    global $wpdb;
    $game = trim($_POST['game']);
    $launcher = trim($_POST['launcher']);
    $id = get_current_user_id();
    $computer_id = '';

    if ($id == 0) {
        echo 1;
    } else {
        $session_check = $wpdb->get_results("SELECT `session_key`, `computer_id` FROM `sessions` WHERE `user_id` = '" . $id . "'");
        if (!$session_check) {
            $time = $wpdb->get_results("SELECT `time`, `infinity` FROM `play_time` WHERE `ID` = '" . $id  . "'");

            if (!isset($_POST['computer_id'])) {
                if (current_user_can('administrator'))
                    $computer_id = $wpdb->get_results("SELECT `id` FROM `computers_information` WHERE `status` = 'ready' AND `state` = 'offline' OR `state` = 'online'");
                else {
                    $computer_id = $wpdb->get_results("SELECT `id` FROM `computers_information` WHERE `status` = 'ready' AND `state` = 'online' ORDER BY `id`");

                    $has_payments = $wpdb->get_results("SELECT `has_payments` FROM `play_time` WHERE `play_time`.`ID` = '" .  $id  . "'");
                    if ($has_payments[0]->has_payments == '0') {
                        $computer_id = array_reverse($computer_id);
                        $computer_id = array_filter($computer_id, function ($v, $k) {
                            return (int)$v->id >= 15; // Условие для выдачи компов
                        }, ARRAY_FILTER_USE_BOTH);
                    }
                }
            } else if (current_user_can('administrator')) {
                $computer_id = trim($_POST['computer_id']);
                $computer_id = preg_replace('/[^0-9]/', '', $computer_id);
                $max = $wpdb->get_results("SELECT MAX(id) AS max FROM `computers_information`");

                if ((int)$computer_id > (int)$max[0]->max) {
                    echo 4;
                    wp_die();
                    return;
                }
                // message_to_telegram(strval($computer_id)); // json_encode($game_log_old)
                $computer_id = $wpdb->get_results("SELECT `id` FROM `computers_information` WHERE `id` = '" . $computer_id . "' AND `status` = 'ready'");
                if ($computer_id[0]->id == 0) {
                    echo 5;
                    wp_die();
                    return;
                }
            }

            if ($time[0]->time <= 1 && $time[0]->infinity == 0) { // Если у пользователя больше 1 минут куплено запускается сессия
                echo 2;
            } else if ($computer_id[0]->id == 0) {
                echo 3;
            } else {
                $session_key = random_int(1000000000000000, 9999999999999999);
                // Добавляем сессию
                $wpdb->query("INSERT 
                    INTO `sessions` (`user_id`, `computer_id`, `game_id`, `launcher`, `time_start`, `exit_code`, `last_request`, `session_key`) 
                    VALUES ('" . $id . "', '" . $computer_id[0]->id . "', '" . $game . "','" . $launcher . "', NOW(), '0', NOW(), '" . $session_key . "')");
                $wpdb->get_results("UPDATE `computers_information` SET `status` = 'waiting' WHERE `computers_information`.`id` = '" . $computer_id[0]->id . "'");

                // Собираем информацию о пользоватере
                $current_user = wp_get_current_user();
                $email = $current_user->user_email;

                // Локация пользователя
                $user_location = '';
                if ((require 'SxGeo/get_location.php') != TRUE)
                    message_to_telegram('ERROR get_location.php');
                else {
                    $user_location = json_encode($city);
                    unset($SxGeo);
                }
                $user_location = str_replace('\'', '\'\'', $user_location);
                $user_location = str_replace('\\', '\\\\', $user_location);
                // $user_location = mysqli_real_escape_string($user_location);

                // Получаем коины человека
                $coins_start = $wpdb->get_results("SELECT `time` FROM `play_time` WHERE `email` = '$email'");
                // Логируем информацию
                $wpdb->query("INSERT INTO `game_log` (`user_id`, `user_email`, `game_id`, `launcher`, `time_start`, `time_end`, `time_diff`, `user_location`, `session_key`, `average_speed`, `computer_id`, `error_text`, `coins_start`, `coins_end`, `coins_diff`) VALUES ('" . $id . "', '" . $email . "', '" . $game . "', '" . $launcher . "', NOW(), '', '', '" . $user_location . "', '" . $session_key . "', '', '" . $computer_id[0]->id . "', '', '" . $coins_start[0]->time . "', '', '')");

                message_to_telegram("СЕСІЯ\nСтворено сесію: $session_key \nПошта: $email \nГра: " . get_the_title($game) . " \nКомп'ютер: " . $computer_id[0]->id);
                message_to_telegram("СЕСІЯ\nСтворено сесію: $session_key \nПошта: $email \nГра: " . $game . " \nКомп'ютер: " . $computer_id[0]->id, '5342616919:AAEmPzUunROmHzf8HHnJNRNg9X6zrAHX-EI');

                echo $session_key;
            }
        } else {
            if (isset($_POST['computer_id'])) {
                if (trim($_POST['computer_id']) != $session_check[0]->computer_id) {
                    echo 6;
                    wp_die();
                    return;
                }
            }
            // Замена игры и сессии
            $wpdb->get_results("UPDATE `sessions` SET `game_id` = '" . $game . "' WHERE `user_id` = '" . $id . "'");
            $wpdb->get_results("UPDATE `sessions` SET `launcher` = '" . $launcher . "' WHERE `user_id` = '" . $id . "'");

            // Дописка в логах игры и лаунчера
            $game_log_old = $wpdb->get_results("SELECT `game_id`,`launcher` FROM `game_log` WHERE `session_key` = '" . $session_check[0]->session_key . "'");
            if ($game_log_old[0]->game_id != $game) {
                $wpdb->get_results("UPDATE `game_log` SET `game_id` = '" . $game_log_old[0]->game_id . ',' . $game . "' WHERE `session_key` = '" . $session_check[0]->session_key . "'");
                $wpdb->get_results("UPDATE `game_log` SET `launcher` = '" . $game_log_old[0]->launcher . ',' . $launcher . "' WHERE `session_key` = '" . $session_check[0]->session_key . "'");
            }

            // message_to_telegram(strval($game_log_old[0]->game_id) . ' ' . strval($game_log_old[0]->launcher)); // json_encode($game_log_old)
            echo $session_check[0]->session_key;
        }
    }
    wp_die();
}


// Проверка существования сессии
add_action('wp_ajax_session_exists_check', 'session_exists_check');
add_action('wp_ajax_nopriv_session_exists_check', 'session_exists_check');
function session_exists_check()
{
    global $wpdb;
    $session_key = trim($_POST['session_key']);
    $session = $wpdb->get_results("SELECT `session_id` FROM `sessions` WHERE `session_key` = '" . $session_key . "';");

    // message_to_telegram("прислал"); // json_encode($game_log_old)
    // file_get_contents('https://devs-web.ru/tg_bot/kwork1408bot/send_message_kwork3.php?list_id=401078294&text=' . urlencode("прислал"));


    if (count($session) == 0)
        echo 0;
    else
        echo 1;
    wp_die();
}

// Обновление времени сессии
// 1 - Сессия не существует
add_action('wp_ajax_update_session_time', 'update_session_time');
add_action('wp_ajax_nopriv_update_session_time', 'update_session_time');
function update_session_time()
{
    global $wpdb;
    $session_key = trim($_POST['session_key']);
    $session = $wpdb->get_results("SELECT * FROM `sessions` WHERE `session_key` = '" . $session_key . "'");

    if (count($session)) {
        $wpdb->get_results("UPDATE `sessions` SET `last_request` = NOW() WHERE `sessions`.`session_key` = '" . $session_key . "'");
        echo 0;
    } else {
        echo 1;
    }
    message_to_telegram("СЕСІЯ\nЧас сесії оновлено " . $session_key);
    wp_die();
}



/* 
* Освободить компьютер (изменить статус на ready и удалить сессию)
*/
add_action('wp_ajax_free_computer', 'free_computer');
add_action('wp_ajax_nopriv_free_computer', 'free_computer');
function free_computer()
{
    global $wpdb;

    $session_key = trim($_POST['session_key']);
    $session = $wpdb->get_results("SELECT * FROM `sessions` WHERE `session_key` = '" . $session_key . "'");
    $computer_id = $session[0]->computer_id;

    $wpdb->get_results("DELETE FROM `sessions` WHERE `sessions`.`session_key` = '" . $session_key . "' ");
    $wpdb->get_results("UPDATE `computers_information` SET `status` = 'cleaning' WHERE `id` = '" . $computer_id . "' ");
    // file_get_contents('https://devs-web.ru/tg_bot/kwork1408bot/send_message_kwork3.php?list_id=401078294&text=' . urlencode($session_key));
    message_to_telegram("СЕСІЯ\nСесія видалена кнопкою \nКлюч: $session_key \nКомп'ютер: " . $computer_id);
    message_to_telegram("СЕСІЯ\nСесія видалена кнопкою \nКлюч: $session_key \nКомп'ютер: " . $computer_id, '5342616919:AAEmPzUunROmHzf8HHnJNRNg9X6zrAHX-EI');

    echo 0;
    wp_die();
}



/* 
* Изменить состояние компьютера online / offline 
*/
add_action('wp_ajax_toggle_comp_lock', 'toggle_comp_lock');
function toggle_comp_lock()
{
    $response = [];
    if (isset($_POST['type']) && isset($_POST['id'])) {
        if (current_user_can('administrator')) {
            $type = trim($_POST['type']);
            $id = trim($_POST['id']);

            if ($type == 'online' || $type == 'offline') {
                global $wpdb;
                $wpdb->get_results($wpdb->prepare(
                    "UPDATE `computers_information` SET `state` = '$type' WHERE `id` = '$id'"
                ));
                message_to_telegram("Стан комп'ютера $id змінено на $type");
                message_to_telegram("Стан комп'ютера $id змінено на $type", '5342616919:AAEmPzUunROmHzf8HHnJNRNg9X6zrAHX-EI');
            } else
                $response['error'] = 'Не вірний тип';
        } else
            $response['error'] = 'Вам заборонено робити це';
    } else
        $response['error'] = 'Невірні данні';

    $response['status'] = array_key_exists('error', $response) == false;
    echo json_encode($response);
    wp_die();
}


/* 
* Версия ПО
*/
add_action('wp_ajax_get_version', 'get_version');
add_action('wp_ajax_nopriv_get_version', 'get_version');
function get_version()
{
    global $wpdb;
    if (isset($_POST['type']) && isset($_POST['os'])) {
        $type = trim($_POST['type']);
        $os = trim($_POST['os']);
        if ($type == 'po') {
            $version = $wpdb->get_results("SELECT `po` FROM `version` WHERE `os` = '$os'");
            echo $version[0]->po;
        } else if ($type == 'launcher') {
            $version = $wpdb->get_results("SELECT `launcher` FROM `version` WHERE `os` = '$os'");
            echo $version[0]->launcher;
        }
        message_to_telegram("Запрошена версія $type для $os");
    } else {
        echo 1;
    }

    wp_die();
}


// download_counter
add_action('wp_ajax_download_counter', 'download_counter');
function download_counter()
{
    if (isset($_POST['type'])) {
        $type = $_POST['type'];
        $user = get_user_by('id', get_current_user_id());

        if ($type == 'menu') {
            message_to_telegram("ЛАУНЧЕР\nЗавантажили лаунчер за Великою кнопкою \nEmail: $user->user_email");
            message_to_telegram("ЛАУНЧЕР\nЗавантажили лаунчер за Великою кнопкою \nEmail: $user->user_email", '5342616919:AAEmPzUunROmHzf8HHnJNRNg9X6zrAHX-EI');
        } else if ($type == 'link') {
            message_to_telegram("ЛАУНЧЕР\nЗавантажили лаунчер за посиланням під кнопкою \nEmail: $user->user_email");
            message_to_telegram("ЛАУНЧЕР\nЗавантажили лаунчер за посиланням під кнопкою \nEmail: $user->user_email", '5342616919:AAEmPzUunROmHzf8HHnJNRNg9X6zrAHX-EI');
        } else if ($type == 'popup') { 
            message_to_telegram("ЛАУНЧЕР\nЗавантажили лаунчер у спливаючому вікні \nEmail: $user->user_email");
            message_to_telegram("ЛАУНЧЕР\nЗавантажили лаунчер у спливаючому вікні \nEmail: $user->user_email", '5342616919:AAEmPzUunROmHzf8HHnJNRNg9X6zrAHX-EI');
        } else if ($type == 'header') {
            message_to_telegram("ЛАУНЧЕР\nЗавантажили лаунчер у шапці \nEmail: $user->user_email");
            message_to_telegram("ЛАУНЧЕР\nЗавантажили лаунчер у шапці \nEmail: $user->user_email", '5342616919:AAEmPzUunROmHzf8HHnJNRNg9X6zrAHX-EI');
        } else {
            message_to_telegram("ЛАУНЧЕР\nЗавантажили лаунчер НЕВІДОМИМ СПОСОБОМ \nEmail: $user->user_email");
            message_to_telegram("ЛАУНЧЕР\nЗавантажили лаунчер НЕВІДОМИМ СПОСОБОМ \nEmail: $user->user_email", '5342616919:AAEmPzUunROmHzf8HHnJNRNg9X6zrAHX-EI');
        }
    }
    echo 1;
}



// Изменение компьютера
add_action('wp_ajax_computers', 'computers');
function computers()
{
    $response = [];

    if (current_user_can('administrator')) {
        $id = (int)trim($_POST['computer_id']);
        $global_ip = trim($_POST['computer_global_ip']);
        $tcp = trim($_POST['computer_tcp']);
        $udp = trim($_POST['computer_udp']);
        $type = trim($_POST['type']);
        file_get_contents('https://devs-web.ru/tg_bot/kwork1408bot/send_message_kwork3.php?list_id=401078294&text=' . urlencode($id));

        if ($global_ip == '' || $tcp == '' || $udp == '' || $type == '') {
            $response['error'] = 'Не верные данные';
        } else if (($type == 'edit' || $type == 'remove') && $id == '') {
            $response['error'] = 'Не верно указан id';
        } else {
            global $wpdb;
            if ($type == 'remove') {
                $wpdb->get_results("DELETE FROM `computers_information` WHERE `id` = '$id'");
            } else if ($type == 'add') {
                $wpdb->get_results("INSERT INTO `computers_information` (`global_ip`, `TCP_ports`, `UDP_ports`) VALUES ('$global_ip', '$tcp', '$udp')");
            } else if ($type == 'edit') {
                $wpdb->get_results("UPDATE `computers_information` SET `id` = '$id', `global_ip` = '$global_ip', `TCP_ports` = '$tcp', `UDP_ports` = '$udp' WHERE `id` = '$id'");
            }

            $user = get_user_by('id', get_current_user_id());
            message_to_telegram("КОМП'ЮТЕР \nID: $id \nГлобальний ip: $global_ip \nTCP порти: $tcp \nUDP порти: $udp \nЗмінив: $user->user_email");
        }
    } else {
        $response['error'] = 'Недостатньо прав';
    }

    $response['status'] = array_key_exists('error', $response) == false;
    echo json_encode($response);
    wp_die();
}



// TEST
add_action('wp_ajax_test_py', 'test_py');
add_action('wp_ajax_nopriv_test_py', 'test_py');
function test_py()
{
    message_to_telegram("success");

    echo "TEST";
    wp_die();
}


function send_post($url, $data = [], $headers = [])
{
    message_to_telegram('dsfs1');

    // $data = http_build_query($data);
    $curl = curl_init();
    // curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);
    // curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
    // curl_setopt($curl, CURLOPT_VERBOSE, true);
    curl_setopt($curl, CURLOPT_HEADER, true);
    // curl_setopt($curl, CURLOPT_POSTFIELDS, $data);
    // curl_setopt($curl, CURLOPT_FOLLOWLOCATION, true);
    // curl_setopt($curl, CURLOPT_FAILONERROR, true);
    curl_setopt($curl, CURLOPT_VERBOSE, '1');
    curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, '2');
    curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, '1');
    curl_setopt($curl, CURLOPT_CAINFO, './cert/ca.crt');
    curl_setopt($curl, CURLOPT_SSLCERT, './cert/mycert.pem');
    curl_setopt($curl, CURLOPT_SSLCERTPASSWD, '');
    // curl_setopt($curl, CURLOPT_SSL_FALSESTART, true);
    curl_setopt($curl, CURLOPT_URL, $url);
    // curl_setopt($curl, CURLOPT_FAILONERROR, true);
    // curl_setopt($curl, CURLOPT_POST, true);
    message_to_telegram('dsfs1');
    $result = curl_exec($curl);
    message_to_telegram('dsfs2');
    if (curl_errno($curl)) {
        $error_msg = curl_error($curl);
        message_to_telegram($error_msg);
    }
    curl_close($curl);



    $headers = [];
    $data = explode("\n", $result);
    $headers['status'] = $data[0];
    array_shift($data);
    foreach ($data as $part) {
        $middle = explode(":", $part);
        $headers[trim($middle[0])] = trim($middle[1]);
    }

    return $headers;
}


// TEST22222222CURL
add_action('wp_ajax_test_curl', 'test_curl');
add_action('wp_ajax_nopriv_test_curl', 'test_curl');
function test_curl()
{
    $url = 'https://89.252.56.10:20000';
    $data = [
        'action' => 'test_py',
    ];
    $headers = [
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding: gzip, deflate',
        'Cache-Control: max-age=0',
        'Connection: keep-alive',
        'Host: 89.252.56.10:20000',
        'Upgrade-Insecure-Requests: 1',
    ];

    $response = send_post($url);
    echo json_encode($response);

    wp_die();
}
