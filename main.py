from datetime import datetime, timedelta

from icalendar import Calendar

CAL_IN_PATH = 'path/to/in_cal.ics'
CAL_OUT_PATH = 'path/to/out_cal.ics'


def timedelta_from_frequ(freq_str, cnt):
    if freq_str == 'DAILY':
        return timedelta(days=cnt)
    elif freq_str == 'WEEKLY':
        return timedelta(weeks=cnt)
    elif freq_str == 'MONTHLY':
        return timedelta(months=cnt)
    else:
        raise ValueError(f"Frequency {freq_str} not recognised")


def happens_after_today(dt):
    dt_date = datetime(dt.year, dt.month, dt.day)

    return dt_date > datetime.today()


def get_ongoing_events_of_calendar():
    g = open(CAL_IN_PATH, 'r')
    cal = Calendar.from_ical(g.read())

    events = []
    event_uids_to_keep = set()
    for component in cal.walk():
        if component.name == "VEVENT":

            # recurring event
            if component.get('RRULE') is not None:
                if 'UNTIL' in component.get('RRULE') and not happens_after_today(component.get('RRULE')['UNTIL'][0]):
                    continue

                if 'COUNT' in component.get('RRULE'):
                    count = component.get('RRULE')['COUNT'][0]
                    freq_str = component.get('RRULE')['FREQ'][0]
                    end_date = component.get('DTEND').dt
                    last_date = end_date + timedelta_from_frequ(freq_str, count)
                    if not happens_after_today(last_date):
                        continue

            elif not happens_after_today(component.get('DTEND').dt):
                continue

            ev_uid = component.get('UID')
            event_uids_to_keep.add(ev_uid)
            print(component.get('summary'))
            events.append(component)

        elif component.name == "VALARM":
            ev_uid = component.get('UID')

            if ev_uid not in event_uids_to_keep:
                continue

            event_uids_to_keep.remove(ev_uid)
            events.append(component)

        else:
            # component of other type
            pass

    print(len(event_uids_to_keep))

    return events


def create_new_calendar_from_events(events):
    cal = Calendar()

    for event in events:
        cal.add_component(event)

    f = open(CAL_OUT_PATH, 'wb')
    f.write(cal.to_ical())
    f.close()


if __name__ == '__main__':
    events = get_ongoing_events_of_calendar()
    create_new_calendar_from_events(events)



