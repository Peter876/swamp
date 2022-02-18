
import appModuleHandler
import controlTypes
from NVDAObjects.IAccessible import IAccessible
import config
import ui
from scriptHandler import script
import keyboardHandler
import winUser
import speech

changeMouseTracking = False
autoFill = True

class AppModule(appModuleHandler.AppModule):

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.windowClassName == "ThunderRT6FormDC" and obj.role == controlTypes.Role.PANE:
			clsList.insert(0, swampGameWindow)
		if obj.windowClassName == "Edit" and obj.role == controlTypes.Role.EDITABLETEXT and obj.windowControlID == 4900:
			clsList.insert(0, swampChatWindow)

	def event_focusEntered(self, obj, nextHandler):
		global changeMouseTracking
		if config.conf["mouse"]["enableMouseTracking"]:
			config.conf["mouse"]["enableMouseTracking"] = False
			changeMouseTracking = True

	def event_appModule_loseFocus(self):
		global changeMouseTracking
		if changeMouseTracking:
			config.conf["mouse"]["enableMouseTracking"] = True
			changeMouseTracking = False

class swampGameWindow(IAccessible):

	def event_typedCharacter(self, ch):
		return

class swampChatWindow(IAccessible):
	currentCommand = False
	skipChars = 0

	def event_typedCharacter(self, ch):
		if self.skipChars > 0:
			self.skipChars -= 1
			return
		super(swampChatWindow,self).event_typedCharacter(ch)

	def event_valueChange(self):
		if not autoFill: return
		commands = ['/w ','/where ','/me ', '/lootpoints', '/questcredits', '/level ', '/deaths ', '/kick ', '/kills ', '/stats ', '/crates ', '/friend ', '/unfriend ', '/friends ', '/beacon ', '/language', '/scripts', '/track ', '/afk', '/lockerupdate', '/title', '/survivors', '/r ', '/roll', '/fw ', '/alert', '/channel', '/voices', '/vol-refresh', '/mute', '/unmute', '/setshow', '/testshow', '/confirmshow', '/show', '/reset', '/time', '/report', '/lootrank']
		text = self.value
		template = '{command}. Press space key for insert.'

		if not text.startswith('/') or len(text) == 1 or self.value[-1:].isspace(): return

		buffer = False

		for command in commands:
			if command == self.value: continue

			if command.find(text) >= 0:
				buffer = command
				if command == self.currentCommand: break
				message = template.format(command=command.rstrip())
				ui.message(message)
				break
		self.currentCommand = buffer

	@script(gesture="KB:space")
	def script_insertCommand(self,gesture):
		if self.currentCommand == False or not autoFill:
			gesture.send()
			return
		text = self.currentCommand[len(self.value):]
		message = "{command} inserted".format(command=self.currentCommand)
		ui.message(message)
		speech.clearTypedWordBuffer()
		chars = 0
		for symbol in text:
			self.isAuto = True
			mod, key = winUser.VkKeyScanEx(symbol, keyboardHandler.getInputHkl())
			keyboardHandler.KeyboardInputGesture([], key, 0, False).send()
			chars += 1
		self.currentCommand = False
		self.skipChars = chars

	@script(gesture="KB:nvda+V")
	def script_speakCurrentCommand(self, gesture):
		if self.currentCommand == False or not autoFill:
			ui.message("No command")
		else:
			ui.message(self.currentCommand)

	@script(gesture="KB:nvda+a")
	def script_autoFillToggle(self, gesture):
		global autoFill
		if autoFill:
			autoFill = False
			self.currentCommand = False
			ui.message("Auto fill off")
		else:
			autoFill = True
			ui.message("Auto fill on")

