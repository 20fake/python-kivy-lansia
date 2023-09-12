from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.pickers import MDTimePicker, MDDatePicker
from kivymd.uix.list import ThreeLineAvatarIconListItem
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivymd.toast.kivytoast.kivytoast import toast
import sqlite3
import datetime
from kivy.uix.widget import Widget
from plyer import stt
from plyer import tts
from kivy.properties import StringProperty
from kivy.core.window import Window


# aktivasi baris ini untuk simulasi
# Window.size = (350, 550)

#aktviasi baris di bawah untuk install android
from android.permissions import request_permissions, Permission


class ListItemWithCheckBox(ThreeLineAvatarIconListItem):
    """Check Box and Trash Icon function"""
    def __init__(self, pk=None, **kwargs):
        super().__init__(**kwargs)
        # state a pk which we shall use link the list items with the database primary keys
        self.pk = pk

    def removeitem(self, taskid):
        conn = sqlite3.connect('reminder.db')
        c = conn.cursor()
        c.execute("DELETE FROM reminder WHERE id=?", (taskid,))
        conn.commit()
        conn.close()

    def delete_item(self, the_list_item):
        '''Delete the task'''
        self.parent.remove_widget(the_list_item)
        self.removeitem(the_list_item.pk)# Here


class HomeScreen(MDScreen):
    name = "homescreen"

    def start_listening(self):
        hour = int(datetime.datetime.now().hour)
        
        if hour >= 0 and hour <= 11:
            tts.speak("Good morning")
        elif hour > 11 and hour < 15:
            tts.speak("good afternoon")
        elif hour >= 15  and hour < 18:
            tts.speak("good evening")

        tts.speak("What can I help you")

        if stt.listening:
            self.stop_listening()
            return

        stt.start()

        Clock.schedule_interval(self.check_state, 1 / 10)

    def stop_listening(self):
        stt.stop()
        self.update()

        Clock.unschedule(self.check_state)

    def check_state(self, dt):
        if not stt.listening:
            self.stop_listening()

    def update(self):
        query = stt.results
        nowtime = datetime.datetime.now().strftime("%H:%M:%S")

        if "hello" in query:
            tts.speak("Hello, How are you?")
            self.ids.labelteks.text = str("Hello, how are you?")

        elif "I'm good" in query:
            tts.speak("Great, Keep it Up!")
            self.ids.labelteks.text = str("Great, keep it up!")

        elif "good morning" in query:
            tts.speak("have you had a breakfast")
            self.ids.labelteks.text = str("have you had a breakfast")

        elif "yes i have breakfast" in query:
            tts.speak("good, let's take a little excersise!")
            self.ids.labelteks.text = str("good, let's take a little excercise")

        elif "what time is it" in query:
            tts.speak("it's" + nowtime + "now")
            self.ids.labelteks.text = str("it's" + nowtime + "now")

        elif "open reminder" in query:
            tts.speak("opening reminder")
            self.manager.transition.direction = "left"
            self.manager.current = "reminderscreen"

        elif "add reminder" in query:
            tts.speak("add reminder")
            self.manager.transition.direction = "left"
            self.manager.current = "addreminderscreen"


class ReminderScreen(MDScreen):
    name = "reminderscreen"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.show_item)

    def show_item(self, *args):
        conn = sqlite3.connect('reminder.db')
        c = conn.cursor()
        records = c.execute("SELECT * FROM reminder").fetchall()
        conn.commit()
        conn.close()

        if records != []:
            for i in records:
                reminder_items = ListItemWithCheckBox(
                    pk=i[0], text = i[1],
                    secondary_text = i[2],
                    tertiary_text = i[3]
                    )
                self.manager.get_screen('reminderscreen').ids.container.add_widget(reminder_items)
            
    def home_screen(self, *args):
        self.manager.transition.direction = "right"
        self.manager.current = "homescreen"
    
    def move_add_screen(self, *args):
        self.manager.transition.direction = "left"
        self.manager.current = "addreminderscreen"

    def delete_all(self, *args, the_list_item):
        deleteall = ListItemWithCheckBox()
        deleteall.delete_all_item(the_list_item)


class AddReminderScreen(MDScreen):
    name = "addreminderscreen"

    sound = SoundLoader.load('alarm.wav')
    soundmakan = SoundLoader.load('makan.wav')
    soundobat = SoundLoader.load('minum_obat.wav')
    soundolahraga = SoundLoader.load('olahraga.wav')
    volume = 0

    time_dialog = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        conn = sqlite3.connect('reminder.db')  # Hubungkan database
        c = conn.cursor()
        c.execute("CREATE TABLE if not exists reminder(id integer PRIMARY KEY AUTOINCREMENT, title TEXT, alarm TEXT, date TEXT, note TEXT)")
        c.execute("CREATE TABLE if not exists warning(id integer PRIMARY KEY, nama_pengingat TEXT)")
        c.execute("INSERT INTO warning(nama_pengingat) VALUES (:first)",
                {
                        'first': "satu",
                    })
        conn.commit()
        conn.close()

        self.time_dialog = MDTimePicker()  # inisialisasi
        self.date_dialog = MDDatePicker()  # inisialisasi
        Clock.schedule_interval(self.alarm, 1)  # schedule the alarm function for every one second

    def time_picker(self):
        self.time_dialog.bind(on_save = self.schedule)
        self.time_dialog.open()

    def schedule(self, *args):
        self.ids.alarm_timed.text = str(self.time_dialog.time)

    def save_date(self, instance, value, date_range):
        self.ids.date_time.text = str(value)

    def date_picker(self):
        self.date_dialog.bind(on_save = self.save_date)
        self.date_dialog.open()

    def checkbox_makan(self, instance, value):
        print(value)
        if value == True:
            self.ids.tambah_jenis_alarm.text= "makan"
        else:
            self.ids.tambah_jenis_alarm.text= ""
    
    def checkbox_minumobat(self, instance, value):
        print(value)
        if value == True:
            self.ids.tambah_jenis_alarm.text= "minum obat"
        else:
            self.ids.tambah_jenis_alarm.text= ""

    def checkbox_olahraga(self, instance, value):
        print(value)
        if value == True:
            self.ids.tambah_jenis_alarm.text= "olahraga"
        else:
            self.ids.tambah_jenis_alarm.text= ""

    def save_reminder(self, *args):
        self.ids.title_add.text = str(self.ids.title_add.text)
        self.ids.alarm_timed.text = str(self.time_dialog.time)
        self.ids.date_time.text = str(self.ids.date_time.text)
        self.ids.tambah_jenis_alarm.text = str(self.ids.tambah_jenis_alarm.text)

        if self.ids.title_add.text == "":
            toast("Kolom Nama Pengingat Kosong, Harap Diisi")
        else:
            conn = sqlite3.connect("reminder.db")
            c = conn.cursor()
            c.execute("INSERT INTO reminder (title, alarm, date, note) VALUES (:first, :second, :third, :fourth)",
                    {
                        'first':self.ids.title_add.text,
                        'second':self.ids.alarm_timed.text,
                        'third':self.ids.date_time.text,
                        'fourth':self.ids.tambah_jenis_alarm.text
                    })

            conn.commit()
            conn.close()

            self.manager.get_screen('reminderscreen').ids['container'].add_widget(
                ListItemWithCheckBox(
                    text = self.ids.title_add.text,
                    secondary_text = self.ids.alarm_timed.text,
                    tertiary_text = self.ids.date_time.text
                )
            )

        
            self.manager.transition.direction = "right"  # set the direction of the transition before moving to next
            self.manager.current = "reminderscreen"  # move to the home screen

        self.ids.title_add.text = "" # Reempty the add title text field
        self.ids.alarm_timed.text = "" # Reempty the add time text field
        self.ids.date_time.text = "" # Reempty the add time text field
    
    def alarm(self, *args):
        current_time = datetime.datetime.now().strftime("%H:%M:%S %Y-%m-%d")

        conn = sqlite3.connect("reminder.db")
        c = conn.cursor()
        c.execute("SELECT alarm || ' ' || date AS today FROM reminder")
        records = c.fetchall()
        conn.commit()
        conn.close()

        alarms = [record[0] for record in records]
        # print(alarms)

        if str(current_time) in alarms:
            conn = sqlite3.connect("reminder.db")
            c = conn.cursor()
            c.execute("SELECT title FROM reminder where alarm || ' ' || date  == '{}' ".format(str(current_time)))
            self.get_data = c.fetchall()
            print("------------------")
            print(self.get_data)
            conn.commit()
            conn.close()  
            self.get_data =''.join(list(self.get_data[0][0]))
            print("---get data---")
            print (self.get_data)

            conn = sqlite3.connect("reminder.db")
            c = conn.cursor()
            c.execute("INSERT INTO warning(nama_pengingat) VALUES (?)",[self.get_data])
            conn.commit()
            conn.close()

            self.start()

    def start(self, *args):
        self.manager.transition.direction = "left"
        self.manager.current = "ringingscreen"

        current_time = datetime.datetime.now().strftime("%H:%M:%S %Y-%m-%d")
        eat = "makan"
        medic = "minum obat"
        sport = "olahraga"

        conn = sqlite3.connect("reminder.db")
        c = conn.cursor()
        c.execute("SELECT alarm || ' ' || date AS today FROM reminder")
        today_result = c.fetchall()
        conn.commit()
        conn.close()

        hasil = [record[0] for record in today_result]
        print("---hasil---")
        print(hasil)

        if str(current_time) in hasil:
            conn = sqlite3.connect("reminder.db")
            c = conn.cursor()
            c.execute("SELECT note FROM reminder where alarm || ' ' || date  == '{}' ".format(str(current_time)))
            self.get_note = c.fetchall()
            print("------------------")
            print(self.get_note)
            conn.commit()
            conn.close()  
            self.get_note =''.join(list(self.get_note[0][0]))
            print("---get note---")
            print (self.get_note)

            if str(eat) in self.get_note:
                self.soundmakan.play()
                self.soundmakan.loop = True
            elif str(sport) in self.get_note:
                self.soundolahraga.play()
                self.soundolahraga.loop = True
            elif str(medic) in self.get_note:
                self.soundobat.play()
                self.soundobat.loop = True
        else:
            pass

    def stop(self):
        self.soundmakan.stop()
        self.soundolahraga.stop()
        self.soundobat.stop()
        self.volume = 0


class RingingScreen(MDScreen):
    name = "ringingscreen"

    alarmsaja = StringProperty()

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        # Disini ada fungsi untuk ambil data yang tersimpan pada AddReminderScreen (function alarm)

        Clock.schedule_interval(self.data_baru, 1)
    
    def data_baru(self,*args):
        conn = sqlite3.connect("reminder.db")
        c = conn.cursor()
        c.execute("""SELECT * FROM warning ORDER BY id DESC LIMIT 1;""")
        self.get_data = c.fetchall()
        # print(self.get_data)
        conn.commit()
        conn.close()
        teksalarm = [alarmlabel[1] for alarmlabel in self.get_data]
        self.alarmsaja=str(teksalarm[0])

    def stop_ring(self):
        selfstop = AddReminderScreen()
        selfstop.stop()
        self.manager.transition.direction = "right"
        self.manager.current = "homescreen"
    

class CustomScreenManager(MDScreenManager):
    """Screen Manager"""


class GiantApp(MDApp):        
    def build(self):
        screen = Builder.load_file('ui.kv')
        return screen

    def on_start(self):
        request_permissions([Permission.RECORD_AUDIO])

    def on_pause(self):
        return True
    

if __name__ == "__main__":
    GiantApp().run()
