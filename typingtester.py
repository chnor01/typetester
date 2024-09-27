import time
import random
import matplotlib.pyplot as plt
import numpy as np
import csv
import os
import re
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def create_sentences(sentence_length, words_length):
    sentences = []
    file_path = "words_noswear.txt"
    with open(file_path, 'r') as file:
    
        words = [word.strip() for word in file.readlines()]
        
    words_filter = [word for word in words if len(word) >= 3]
    words_regex = words_regex = [word for word in words_filter if re.search("[aeiou]", word)]
    
    for i in range(1000):
        sentence_words = [word for word in words_regex if len(word) >= (words_length-4) and len(word) <= words_length]
        sentence_words = random.sample(sentence_words, sentence_length)
        sentence = " ".join(sentence_words)
        sentences.append(sentence)
    return sentences
        
def create_real_sentences(difficulty):
    sentences = []
    
    file_path = "sentences.txt"
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.readlines()
        
    data_strip = [line.strip() for line in data]
    data_unique = list(set(data_strip))
    words_nonumbers = [word for word in data_unique if not any(char.isdigit() for char in word)]
    data_nospecial = [re.sub("[;:’'!?-]", "", word) for word in words_nonumbers]
 
    for _ in range(1000): 
        random_sentence = random.sample(data_nospecial, difficulty*2)
        sentence_combine = " ".join(random_sentence)
        sentences.append(sentence_combine)
    return sentences


def words_or_sentences():
    global wordsorsentences
    choices = {1: "Real sentences", 2: "Random words"}
    try:
        wordsorsentences = int(entry_wordsorsentences.get())
        if wordsorsentences in [1, 2]:
            label_wordsorsentences.config(text=f"Chose: {choices[wordsorsentences]}")
            button_wordsorsentences.config(state=tk.DISABLED)
               
        else:
            label_wordsorsentences.config(text="Enter 1 or 2.")
            entry_wordsorsentences.delete(0, tk.END)
    
    except ValueError:
        label_wordsorsentences.config(text="Please enter a valid integer.")
        entry_wordsorsentences.delete(0, tk.END) 
        
 
    
def choosediff():
    global sentences
        
    try:
        if (wordsorsentences and num_examples) < 1:
            label_diff.config(text="Please enter values for previous choices first")
            return
        
        diffchoice = int(entry_diff.get())
        if 0 < diffchoice < 4:
            lengths = {1: [4, 10, "easy"], 2: [9, 15, "medium"], 3: [14, 20, "hard"]}
            words_length, sentence_length, diff_text = lengths.get(diffchoice)
            
            if wordsorsentences == 1:
                sentences = create_real_sentences(diffchoice)
                
            elif wordsorsentences == 2:   
                sentences = create_sentences(sentence_length, words_length)
                
            
            label_diff.config(text=f"Difficulty chosen: {diff_text}")
            button_diff.config(state=tk.DISABLED)
            
        else:
            label_diff.config(text="Please enter an integer, 1 to 3.")
            entry_diff.delete(0, tk.END) 
                 
    except ValueError:
        label_diff.config(text="Please enter a valid integer.")
        entry_diff.delete(0, tk.END) 
        

def start_timer(event):
    global start_time
    if event.char.isalpha() and start_time == 0:
        start_time = time.time()
        update_timer()
        
def update_timer():
    global start_time
    if start_time > 0:
        current_time = time.time() - start_time
        timer_label.config(text=f"Time: {round(current_time, 1)} seconds")
        root.after(100, update_timer)

def stop_timer():
    global start_time, elapsedtime
    if start_time > 0:
        elapsedtime = time.time() - start_time
        start_time = 0


def showsent(): 
    
    global origsplit
    
    stop_timer()
    
    text_sentence.config(state="normal")
    
    entry_sentence.bind('<Return>', showsentsubmit)
    entry_sentence.bind('<KeyPress>', start_timer)
    
    entry_sentence.config(state=tk.NORMAL)
    entry_sentence.delete(0, tk.END) 
    
    text_sentence.delete("1.0", tk.END)
    button_submit.config(state=tk.NORMAL)
    
    try:
        original_text = random.choice(sentences)
        origsplit = original_text.split()
        text_sentence.insert("1.0", original_text)
    except:
        text_sentence.insert("1.0", "No data found")
    
    text_sentence.config(state="disabled")
    
def char_pos(index, words, end=False):
    pos = 0
    if end:
        pos += len(words[index])
    for i in range(index):
        pos += len(words[i]) + 1
    return pos

    
def showsentsubmit(event=None):
    global current_example, counter, acc_all, wpm_all, elapsedtime, typedtextsplit
    
    text_sentence.config(state="normal")
    typed_text = entry_sentence.get()
    if not typed_text or any(char.isdigit() for char in typed_text):
        return 
    
    typedtextsplit = typed_text.split()
    stop_timer()
    
    counter = 0
    tag_correct = "correct"
    tag_incorrect = "incorrect"
    
    for i in range(len(origsplit)):
        start = char_pos(i, origsplit)
        end = char_pos(i, origsplit, True)
        
        if i < len(typedtextsplit) and origsplit[i] == typedtextsplit[i]:
            counter += 1
            tag = tag_correct
        else:
            tag = tag_incorrect
        
        text_sentence.tag_add(tag, f"1.{start}", f"1.{end}")

    text_sentence.tag_config(tag_correct, foreground="green")
    text_sentence.tag_config(tag_incorrect, foreground="red")
    
    text_sentence.config(state="disabled")

    accuracy = counter / len(origsplit)  
    words_per_min = len(typedtextsplit) / (elapsedtime / 60)
    
    if words_per_min < 600:
        acc_all.append(accuracy)
        wpm_all.append(words_per_min)
        label_acc_curr.config(text=f"Accuracy: {round(accuracy*100, 1)}%")
        label_wpm_curr.config(text=f"WPM: {round(words_per_min, 1)}")
        current_example += 1
        timer_label.config(text=f"Elapsed time: {round(elapsedtime, 1)} seconds\nTyping test {current_example-1}/{num_examples} completed!")
    
    else:
        label_wpm_curr.config(text=f"WPM {round(words_per_min, )} is too high... cheating or superhuman?")
        return
    
    
    if current_example > num_examples:
        button_submit.config(state=tk.DISABLED)
        button_gen.config(state=tk.DISABLED)
        plot_tables()
        highscores()
        savestats()
        
    button_submit.config(state=tk.DISABLED)
    entry_sentence.config(state=tk.DISABLED)
    entry_sentence.unbind('<Return>') 
    entry_sentence.unbind('<Key>', start_timer)
    

        
def get_num_examples():
    global num_examples
    try:
        num_examples = int(entry_numexamples.get())
        if 0 < num_examples < 20:
            label_numexamples.config(text=f"{num_examples} text examples chosen.")
            button_numexamples.config(state=tk.DISABLED)
        else:
            label_numexamples.config(text="Please enter a positive integer between 1 and 19.")
            entry_numexamples.delete(0, tk.END)
    except ValueError:
        label_numexamples.config(text="Please enter a valid integer.")
        entry_numexamples.delete(0, tk.END) 

def savestats():
    global data_zip
    
    data_zip = list(zip(acc_all, wpm_all))

    with open("statistics.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data_zip)
        
  
def create_bar_window():
    window_typingtest = tk.Tk()
    window_typingtest.title("Plots of typing test (bar chart)")
    window_typingtest.geometry("800x600")
    return window_typingtest
        
def plot_tables():
    global window_bargraph
    
    average_wpm = np.mean(wpm_all)
    average_acc = np.mean(acc_all)
    
    if len(wpm_all) < 1 or len(acc_all) <1:
        return
    
    window_bargraph = create_bar_window()
    number_examples = range(1, len(wpm_all) + 1)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    ax1.bar(number_examples, wpm_all, color="b", label="WPM")
    ax1.axhline(y=average_wpm, color='r', linestyle="dashed", label=f"Average WPM = {round(average_wpm, 1)}")
    ax1.set_ylabel("Words per Minute (WPM)")  
    ax1.set_xticks(number_examples)
    ax1.legend()
    
    ax2.bar(number_examples, acc_all, color="b", label="Accuracy")
    ax2.axhline(y=average_acc, color="r", linestyle="dashed", label=f"Average Accuracy = {round(average_acc, 1)}")
    ax2.set_xlabel("Typing test number") 
    ax2.set_ylabel("Accuracy")
    ax2.set_xticks(number_examples)  
    ax2.legend()
    
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=window_bargraph)
    canvas_plot = canvas.get_tk_widget()
    canvas_plot.pack()
    
    
    
def loadstats():
    file_path = "statistics.csv"
    if os.path.isfile(file_path):
        with open(file_path, "r", newline="") as file:
            data_reader = csv.reader(file)
            data_load = []
        
            for row in data_reader:
                accuracy, wpm = map(float, row)
                data_load.append((accuracy, wpm))
                
        accs_saved, wpms_saved = zip(*data_load)
        return accs_saved, wpms_saved
    return

    

def highscores(): 
    load_stats = loadstats()
    if loadstats():
        
        wpm_win = ["How much coffee have you been drinking?!", "Warp speed!", "Keyboard is on fire!", "Faster than the speed of light!", "We got Usain Bolt over here!"]
        acc_win = ["Accurate like a brain surgeon!", "Sharpshooter ahead!", "Bullseye!", "Laser-level precision!"]
        wpm_lose = ["Slow and steady wins the race - you got this!", "PROTIP: do some hand stretching!", "It must be early in the morning!", "I've seen turtles type faster!"]
        acc_lose = ["Are you even looking at your keyboard?!", "Typos are OK, keep practicing!", "Better luck next time!", "Focus on the words!" ]
        wpm_win_rand = random.choice(wpm_win)
        acc_win_rand = random.choice(acc_win)
        wpm_lose_rand = random.choice(wpm_lose)
        acc_lose_rand = random.choice(acc_lose)
        
        accs_saved, wpms_saved = load_stats
        acc_max_saved = max(accs_saved)
        wpm_max_saved = max(wpms_saved)  
    
        acc_max_curr = max(acc_all)
        wpm_max_curr = max(wpm_all)
    
        if acc_max_curr > acc_max_saved: 
            label_acc_max.config(text=f"{acc_win_rand} New accuracy highscore! {round(acc_max_curr, 2)*100}%")
        elif acc_max_curr == 1 or acc_max_saved == 1:
            label_acc_max.config(text="Accuracy high score: 100%")
        else:
            label_acc_max.config(text=f"{acc_lose_rand} Current accuracy highscore: {round(acc_max_saved, 2)*100}%")
     
        
        if wpm_max_curr > wpm_max_saved:
            label_wpm_max.config(text=f"{wpm_win_rand} New WPM highscore! {round(wpm_max_curr, 1)}")
        else:
            label_wpm_max.config(text=f"{wpm_lose_rand} Current WPM highscore: {round(wpm_max_saved, 1)}")
            
         
        

def create_linegraph_window():
    window_graph = tk.Tk()
    window_graph.title("Plot of historical data (line graph)")
    window_graph.geometry("800x600")
    return window_graph

                
def plothistorical():
    
    global window_linegraph
    load_stats = loadstats()
    if loadstats():
        accs_saved, wpms_saved = load_stats
        window_linegraph = create_linegraph_window()
        acc_hist_avg = np.mean(accs_saved)
        wpm_hist_avg = np.mean(wpms_saved)
        
        number_examples = range(1, len(accs_saved) + 1)
    
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        ax1.plot(number_examples, accs_saved, label= "Accuracy", marker=".", color="blue")
        ax1.axhline(acc_hist_avg, color= "green", linestyle="dashed", label=f"Average Accuracy: {round(acc_hist_avg, 2)}")
        ax1.set_ylabel("Accuracy")
        ax1.set_xticks(number_examples)
        ax1.legend()
        
        ax2.plot(number_examples, wpms_saved, label="WPM",  marker="." , color="red")
        ax2.axhline(wpm_hist_avg, color="orange", linestyle="dashed", label=f"Average WPM: {round(wpm_hist_avg, 1)}")
        ax2.set_xlabel("Typing test number")
        ax2.set_ylabel("WPM")
        ax2.set_xticks(number_examples)
        ax2.legend()
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=window_linegraph)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()

    
def windows_destroy():
    try:
        window_linegraph.destroy()
        window_bargraph.destroy()
        
    except tk.TclError as e:
        print(f"Error: {e}")
    
def gamereset():
    global sentences, wpm_all, acc_all, data_zip, current_example, start_time, num_examples, wordsorsentences, diffchoice
    wpm_all = []
    acc_all = []
    data_zip = []
    sentences = []
    
    num_examples = 0
    wordsorsentences = 0
    diffchoice = 0
    
    current_example = 1
    start_time = 0  
    
    text_sentence.config(state="normal")
    text_sentence.delete("1.0", tk.END)
    text_sentence.config(state="disabled")
    
    for entry in all_entries:
        entry.config(state=tk.NORMAL)
        entry.delete(0, tk.END)
    
    for button in all_buttons:
        button.config(state=tk.NORMAL)
        
    for i in range(len(all_labels)):
        all_labels[i].config(text=all_text[i])
        
    for label in all_labels_stat:
        label.config(text="")
        
    timer_label.config(text="Time: 0.00 seconds")
    windows_destroy()
    
    
def exitapp():
    root.destroy()
    windows_destroy()
        
    

acc_all = []
wpm_all = []
data_zip = []
current_example = 1
start_time = 0

diffchoice = 0
wordsorsentences = 0
num_examples = 0


root = tk.Tk()
root.title("Typing Test")
root.configure(bg='#579eff')
root.geometry("1280x1280")

label_welcome = tk.Label(root, text="Welcome to the TypingTester!")
label_welcome.pack()
label_welcome.config(font=("Helvetica", 16))  
label_welcome.place(x=100, y=100)

label_numexamples = tk.Label(root, text="Enter the number of text examples:")
label_numexamples.pack()
label_numexamples.config(font=("Helvetica", 16))  

entry_numexamples = tk.Entry(root, font=('Helvetica', 16))
entry_numexamples.pack()

button_numexamples = tk.Button(root, text="Confirm", command=get_num_examples)
button_numexamples.pack()
button_numexamples.config(width=10, height=2)


label_wordsorsentences = tk.Label(root, text="1. Real sentences\n2. Random words")
label_wordsorsentences.pack()
label_wordsorsentences.config(font=("Helvetica", 16))  

entry_wordsorsentences = tk.Entry(root, font=('Helvetica', 16))
entry_wordsorsentences.pack()


button_wordsorsentences = tk.Button(root, text="Confirm", command=words_or_sentences)
button_wordsorsentences.pack()
button_wordsorsentences.config(width=10, height=2)


label_diff = tk.Label(root, text="1. Easy\n2. Medium 3. Hard\nChoose difficulty of typing test:")
label_diff.pack()
label_diff.config(font=("Helvetica", 16))  

entry_diff = tk.Entry(root, font=('Helvetica', 16))
entry_diff.pack()

button_diff = tk.Button(root, text="Confirm", command=choosediff)
button_diff.pack()
button_diff.config(width=10, height=2)



button_gen = tk.Button(root, text="Generate Typing Test", command=showsent)
button_gen.pack(pady=10)
button_gen.config(width=30, height=2)


text_sentence = tk.Text(root, state="disabled", wrap="word", font=("Helvetica", 16), height=5, width=100)
text_sentence.pack(pady=10)


entry_sentence = tk.Entry(root, font=('Helvetica', 16))
entry_sentence.pack(pady=10)


timer_label = tk.Label(root, text="Time: 0.00 seconds", font=("Helvetica", 16))
timer_label.pack(pady=10)


button_submit = tk.Button(root, text="Submit", command=showsentsubmit)
button_submit.pack(pady=10)
button_submit.config(width=20, height=2)

label_acc_curr = tk.Label(root, text="")
label_acc_curr.pack(pady=10)
label_acc_curr.config(font=("Helvetica", 16))  

label_wpm_curr = tk.Label(root, text="")
label_wpm_curr.pack(pady=10)
label_wpm_curr.config(font=("Helvetica", 16)) 

label_acc_max = tk.Label(root, text="")
label_acc_max.pack(pady=10)
label_acc_max.config(font=("Helvetica", 16)) 


label_wpm_max = tk.Label(root, text="")
label_wpm_max.pack(pady=10)
label_wpm_max.config(font=("Helvetica", 16)) 


window_hist_button = tk.Button(root, text="Plot Graph", command=plothistorical)
window_hist_button.pack(pady=10)
window_hist_button.config(width=20, height=2)
window_hist_button.place(x=1000, y=20)

button_reset = tk.Button(root, text="Play Again", command=gamereset)
button_reset.config(width=20, height=2)
button_reset.place(x=1000, y=100)

button_exit = tk.Button(root, text="Exit Game", command=exitapp)
button_exit.place(x=1200, y=20)


all_entries = [entry_numexamples, entry_wordsorsentences, entry_diff, entry_sentence]
all_buttons = [button_numexamples, button_wordsorsentences, button_diff, button_gen, button_submit, window_hist_button]
all_labels = [label_numexamples, label_wordsorsentences, label_diff]
all_labels_stat = [label_acc_curr, label_wpm_curr, label_acc_max, label_wpm_max]
all_text = ["Enter the number of text examples:", "1. Real sentences\n2. Random words", "1. Easy\n2. Medium 3. Hard\nChoose difficulty of typing test:"]

root.mainloop()


    
   



