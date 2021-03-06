# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import json

import webnotes
from webnotes.utils import cint, formatdate

def get_transaction_list(doctype, start, additional_fields=None):
	# find customer id
	customer = webnotes.conn.get_value("Contact", {"email_id": webnotes.session.user}, 
		"customer")
	
	if customer:
		if additional_fields:
			additional_fields = ", " + ", ".join(("`%s`" % f for f in additional_fields))
		else:
			additional_fields = ""
			
		transactions = webnotes.conn.sql("""select name, creation, currency, grand_total_export
			%s
			from `tab%s` where customer=%s and docstatus=1
			order by creation desc
			limit %s, 20""" % (additional_fields, doctype, "%s", "%s"), 
			(customer, cint(start)), as_dict=True)
		for doc in transactions:
			items = webnotes.conn.sql_list("""select item_name
				from `tab%s Item` where parent=%s limit 6""" % (doctype, "%s"), doc.name)
			doc.items = ", ".join(items[:5]) + ("..." if (len(items) > 5) else "")
			doc.creation = formatdate(doc.creation)
		return transactions
	else:
		return []
		
def get_currency_context():
	return {
		"global_number_format": webnotes.conn.get_default("number_format") or "#,###.##",
		"currency": webnotes.conn.get_default("currency"),
		"currency_symbols": json.dumps(dict(webnotes.conn.sql("""select name, symbol
			from tabCurrency where ifnull(enabled,0)=1""")))
	}

def get_transaction_context(doctype, name):
	customer = webnotes.conn.get_value("Contact", {"email_id": webnotes.session.user}, 
		"customer")
	
	bean = webnotes.bean(doctype, name)
	if bean.doc.customer != customer:
		return { "bean": webnotes._dict({ "doc": webnotes._dict({"name": _("Not Allowed")}) }) }
	else:
		return { "bean": bean }