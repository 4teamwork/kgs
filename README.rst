kgs
===

Provide known good sets of versions used for buildout_.
This system is used for internal and open source projects at 4teamwork_.

.. _buildout: https://pypi.python.org/pypi/zc.buildout/
.. _4teamwork: http://www.4teamwork.ch/


Allergen declaration
--------------------
This README may contain traces of php.


Installation
------------

Add ``http://kgs.example.com/pull.php`` to Github Service Hooks as WebHook URL.


Define a short update script that pulls your changes.

.. code:: php

	<?php $output = shell_exec('git pull'); echo $output; ?>
	
	
Configure apache.

.. code:: apache

	<VirtualHost 10.1.2.3:80>
	    ServerName kgs.example.com

	    ErrorLog logs/kgs.example.com-error.log
	    CustomLog logs/kgs.example.com-access.log combined

	    DocumentRoot /var/www/kgs

	    XBitHack on
	    IndexOptions IgnoreCase FancyIndexing FoldersFirst IconsAreLinks SuppressHTMLPreamble
	    IndexOrderDefault Ascending Name
	    HeaderName "/header.html"
	    ReadmeName "/footer.html"

	    <Directory /var/www/kgs/>
	       Options Indexes FollowSymLinks MultiViews +Includes
	       Order allow,deny
	       Allow from all
	    </Directory>
	</VirtualHost>
