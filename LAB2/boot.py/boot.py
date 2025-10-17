def urldecode(s):
    import ure
    s = s.replace('+', ' ')
    hex_pattern = ure.compile(r'%([0-9A-Fa-f]{2})')
    return hex_pattern.sub(lambda m: chr(int(m.group(1), 16)), s)

while True:
    try:
        conn, addr = s.accept()
        request = conn.recv(2048).decode('utf-8', 'ignore')

        # LED control
        if '/led_on' in request:
            led.value(1)
        elif '/led_off' in request:
            led.value(0)

        # Sensor reads
        t, h = read_dht()
        d = read_distance()
        led_state = "ON" if led.value() else "OFF"

        # LCD show button
        if '/show' in request:
            show_lcd(t, d)

        # Custom LCD text
        if '/send_text' in request:
            try:
                line = request.split('\n')[0]
                path = line.split(' ')[1]
                if '?' in path:
                    qs = path.split('?', 1)[1]
                    if 'msg=' in qs:
                        val = qs.split('msg=', 1)[1]
                        val = val.split('&')[0]
                        val = urldecode(val)
                        lcd.clear()
                        if len(val) <= 16:
                            lcd.putstr(val)
                        else:
                            lcd.putstr(val[:16])
                            lcd.move_to(0, 1)
                            lcd.putstr(val[16:32])
            except:
                pass

        # Send response
        response = webpage(t, h, d, led_state)
        header = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n"
        conn.send(header.encode('utf-8'))
        conn.send(response.encode('utf-8'))
        conn.close()

    except Exception as e:
        try:
            conn.close()
        except:
            pass
        time.sleep(0.1)