#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import linecache
import os
import threading
import time
import logging
from datetime import datetime
from pynput import keyboard
from pynput import mouse

# 等待命令控制（Esc退出  Command+s:开始录制  Command+e:结束录制  Command+p:开始播放）
g_waittingCommandPower = False

# 全局变量
g_mouse = mouse.Controller()
g_recordPower = False
g_mousePress = False
g_preTime = int(time.time())
g_threads = []

g_logFile = os.getcwd() + '/record.log'

FORMAT = "%(asctime)s %(message)s"
logging.basicConfig(filename=g_logFile, level=logging.DEBUG, format=FORMAT)

# 重置日志函数
def resetLog():
	# logFile = os.getcwd() + '/record.log'
	global g_logFile

	if os.path.isfile(g_logFile):
		os.remove(g_logFile)
	else:
		print('not exist log file')

		fp = open(g_logFile, 'a')
		fp.close()


#鼠标事件
def on_move(x, y):
	global g_mousePress

	if g_recordPower:
		if g_mousePress:
			logging.info('1 %f %f', x, y)
		else:
			logging.info('3 %f %f', x, y)

def on_click(x, y , button, press):
	global g_mousePress

	g_mousePress = press
	if press:
		if g_recordPower:
			logging.info('0 %f %f', x, y)
	else:
		if g_recordPower:
			logging.info('2 %f %f', x, y)

# 键盘事件
def on_press(key):
	global g_waittingCommandPower
	global g_recordPower
	global g_preTime

	try:
		if g_waittingCommandPower:
			if format(key.char) == 's':
				resetLog()
				g_recordPower = True
			elif format(key.char) == 'e':
				g_recordPower = False
			elif format(key.char) == 'p':
				g_recordPower = False
				g_preTime = int(time.time())
				readLog(1)
		else:
			if key == keyboard.Key.cmd:
				g_waittingCommandPower = True
	except AttributeError:
		print('special key {0} pressed'.format(key))

def on_release(key):
	global g_waittingCommandPower

	try:
		if key == keyboard.Key.cmd:
			g_waittingCommandPower = False

		if key == keyboard.Key.esc:
			for i in g_threads:
				i.stop()
	except AttributeError:
		print('special key {0} pressed'.format(key))

# 读日志文件
def readLog(row):
	global g_logFile

	if os.path.isfile(g_logFile):
		pass
	else:
		print('not exist log file')

	line = linecache.getline(g_logFile, row)
	if not line:
		linecache.clearcache()
		return

	datas = line.split(" ")

	timeStr = datas[0] + ' ' + datas[1]
	datetimeObj = datetime.strptime(timeStr, "%Y-%m-%d %H:%M:%S,%f")
	objStamp = int(time.mktime(datetimeObj.timetuple()) * 1000.0 + datetimeObj.microsecond / 1000.0)

	global g_preTime
	if row == 1:
		g_preTime = objStamp
	else:
		pass

	currentTime = objStamp
	timeOffset = currentTime - g_preTime
	g_preTime = currentTime

	t = time.time()
	msStamp = int(round(t * 1000))  # 毫秒级时间戳
	timeOffset = timeOffset / 1000;
	print(row, timeOffset, msStamp)

	controlMouse(datas[2], datas[3], datas[4], row)

	threading.Timer(timeOffset, readLog, [row + 1]).start()

def controlMouse(type, strx, stry, row):
	sy = stry.replace('\n', '')
	x = float(strx)
	y = float(sy)

	global g_mouse
	if row == 1:
		g_mouse.position = (x, y)
	else:
		if type == "0":
			g_mouse.press(mouse.Button.left)
		elif type == "1":
			g_mouse.move(x - g_mouse.position[0], y - g_mouse.position[1])
		elif type == "2":
			g_mouse.release(mouse.Button.left)
		elif type == "3":
			g_mouse.move(x - g_mouse.position[0], y - g_mouse.position[1])

# 开启监听
me = mouse.Listener(on_move=on_move, on_click=on_click)
ke = keyboard.Listener(on_press=on_press, on_release=on_release)

g_threads.append(me)
g_threads.append(ke)

for i in g_threads:
	i.start()
for i in g_threads:
	i.join()