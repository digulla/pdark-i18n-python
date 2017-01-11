Python version of my I18N system. Unlike all other I18N systems, this one uses "late translation" and clearly separates between "collecting data for messages" and "displaying messages."

Code always creates "I18N messages" which contain a translation ID plus all the necessary arguments.
Later, when the message is displayed to the user, the actual text is looked up and arguments are properly formatted.

This way, code which creates messages doesn't have to worry how to display it and code which needs to display
messages doesn't have to worry where to get the data from.

Advantages:

* Tests don't depend on the locale. Tests can always rely on the I18N message object.

* Tests don't have to load translations. You can always compare against the translation ID.

* Tests can look at the message arguments.

* Message arguments can be objects.

* Message arguments can be other I18N messages

* Message arguments can be validated

* Translations can be loaded from a wide range of sources

* Only the UI code needs to know the current locale

* Clear separation of concerns: The back end / framework code defines which messages exist and what the arguments are. The front end / UI code defines text sources, lookup strategies, formatters.

* Tools can create reports

	* Where is a message used

	* Which translations exist and which are missing

Disadvantages:

* At fist glance, the separation causes more boiler plate code. When you use the framework in a real project, you'll find that you only have to add a bit of code in a few places.

* I18N messages and all their arguments must be immutable. If you pass the message on and then change the value of an argument, the final message will show the new value.

Features:

* Reports that tell you which text is used where

* Everything is an object, no typos

* Supports different sources for translations (dictionary, text files, JSON, database, custom code)

* Late translation. No log messages in Chinese.

* Easily customizable for different needs

Requirements:

* Python 3