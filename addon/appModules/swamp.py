
import appModuleHandler
import controlTypes
from NVDAObjects.IAccessible import IAccessible
import config
import ui
from scriptHandler import script
import keyboardHandler
import winUser
import api
import speech
import eventHandler

changeMouseTracking = False
autocomplete = True

class AppModule(appModuleHandler.AppModule):

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.windowClassName == "ThunderRT6FormDC" and obj.role == controlTypes.ROLE_PANE:
			clsList.insert(0, swampGameWindow)
		if obj.windowClassName == "Edit" and obj.role == controlTypes.ROLE_EDITABLETEXT and obj.windowControlID == 4900:
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

	@script(gesture="KB:nvda+a")
	def script_autocompleteToggle(self, gesture):
		global autocomplete
		if autocomplete:
			autocomplete = False
			ui.message("Autocomplete off")
		else:
			autocomplete = True
			ui.message("Autocomplete on")

class swampGameWindow(IAccessible):

	def event_typedCharacter(self, ch):
		return

class swampChatWindow(IAccessible):
	currentCommand = False

	def event_typedCharacter(self, ch):
		if eventHandler.isPendingEvents("typedCharacter"): return
		super(swampChatWindow,self).event_typedCharacter(ch)

	def event_valueChange(self):
		if not autocomplete: return
		commands = ['/w ','/where ','/me ', '/lootpoints ', '/questcredits ', '/level ', '/deaths ', '/kills ', '/stats ', '/crates ', '/friend ', '/unfriend ', '/friends ', '/beacon ', '/language', '/scripts', '/track ']
		text = self.value
		template = '{command}. Press space key for insert.'

		if text[0:1] != '/' or len(text) == 1 or self.value[-1:].isspace(): return

		buffer = False
		for command in commands:
			if command[:-1] == self.value:
				buffer = command
				break
			if command == self.value: continue

			if command.find(text) >= 0:
				buffer = command
				if command == self.currentCommand: break
				message = template.format(command=command[:-1])
				ui.message(message)
				break
		self.currentCommand = buffer

	@script(gesture="KB:space")
	def script_insertCommand(self,gesture):
		if self.currentCommand == False:
			gesture.send()
			return
		text = self.currentCommand[len(self.value):]
		message = "{command} inserted".format(command=self.currentCommand)
		ui.message(message)
		speech.clearTypedWordBuffer()
		for symbol in text:
			self.isAuto = True
			mod, key = winUser.VkKeyScanEx(symbol, keyboardHandler.getInputHkl())
			keyboardHandler.KeyboardInputGesture([], key, 0, False).send()
		self.currentCommand = False

	@script(gesture="KB:nvda+V")
	def script_speakCurrentCommand(self, gesture):
		if self.currentCommand == False:
			ui.message("No command")
		else:
			ui.message(self.currentCommand)
