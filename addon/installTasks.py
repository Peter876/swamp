#installTasks.py
#A part of swamp add-on
#Copyright (C) 2020 Eugene Poplavsky <jawhien@gmail.com>

import wx
import gui
import webbrowser
import addonHandler
from versionInfo import version_year, version_major

addonHandler.initTranslation()

donations_url = "https://yoomoney.ru/to/410012216939697"

def onInstall():
	manifest = addonHandler.getCodeAddon().manifest
	try:
		if isinstance(manifest["minimumNVDAVersion"], unicode):
			minVersion = manifest["minimumNVDAVersion"].split(".")
		else:
			minVersion = manifest["minimumNVDAVersion"]
	except NameError:
		minVersion = manifest["minimumNVDAVersion"]

	year = int(minVersion[0])
	major = int(minVersion[1])

	if (version_year, version_major) < (year, major):
		gui.messageBox(_("This version of NVDA is incompatible. To install the add-on, NVDA version {year}.{major} or higher is required. Please update NVDA or download an older version of the add-on here: \n{link}").format(year=year, major=major, link="https://github.com/jawhien/swamp/releases/"), _("Error"), style=wx.OK | wx.ICON_ERROR)
		raise RuntimeError("Incompatible NVDA version")

	# Translators: The text of the dialog shown during add-on installation.
	message = _(""" {name} - this free add-on for NVDA.
You can make a donation to the author to help further development of this add-on and other free software.
You want to make a donation now? For transaction you will be redirected to the website of the developer.""").format(name=manifest['summary'])

	if gui.messageBox(message, _("Request donations for {name}").format(name=manifest['summary']), style=wx.YES_NO|wx.ICON_QUESTION) == wx.YES:
		webbrowser.open(donations_url)
