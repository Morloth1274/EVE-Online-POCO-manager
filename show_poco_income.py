import evelink.api
import evelink.eve

from datetime import datetime
from datetime import date

api = evelink.api.API(api_key=(4380231, 'uRizCWbLX9mOtC57RAObJc7k3ZWNVSzFhAZ1cfTn9QVXlJ4pi9O1KVQTTfYWeDfi'))
corp = evelink.corp.Corp(api)
response = corp.wallet_journal()

#print dir(response.result)

amount_per_planet = {}
amount_per_system = {}
pocos_per_system = {}
handled_journal_ids = []
earliest_time_per_planet = {}
earliest_time_per_system = {}

earliest_id = None
earliest_entry = None

found_new_entry = True
while found_new_entry:

	found_new_entry = False
	for a in response:
		if isinstance(a, list):
			for b in a:
				if isinstance(b, dict):
					journal_id = b["id"]

					if journal_id in handled_journal_ids:
						continue
					handled_journal_ids.append(journal_id)
					found_new_entry = True

					#print b

					timestamp = b["timestamp"]
					ts = datetime.fromtimestamp(timestamp)
					#print ts

					planet = b["reason"]
					planet = planet[16:]

					if planet in earliest_time_per_planet:
						if earliest_time_per_planet[planet] > ts:
							earliest_time_per_planet[planet] = ts
					else:
						earliest_time_per_planet[planet] = ts
						

					system = planet[:planet.rfind(" ")]
					if system in earliest_time_per_system:
						if earliest_time_per_system[system] > ts:
							earliest_time_per_system[system] = ts
					else:
						earliest_time_per_system[system] = ts

					#print "System: ", system, "-- Planet: ", planet, "\n"
					if planet in amount_per_planet:
						amount_per_planet[planet] = amount_per_planet[planet] + b["amount"]
					else:
						amount_per_planet[planet] = b["amount"]
						if system in pocos_per_system:
							pocos_per_system[system] = pocos_per_system[system] + 1
						else:
							pocos_per_system[system] = 1

					if system in amount_per_system:
						amount_per_system[system] = amount_per_system[system] + b["amount"]
					else:
						amount_per_system[system] = b["amount"]

					if earliest_id is None or earliest_id > journal_id:
						earliest_id = journal_id
						earliest_entry = b

					#print b["id"], " -> ", b, "\n"
					#print "Earliest id: ", earliest_id, "\n"

	#print "Earliest entry: ", earliest_entry, "\n"
	response = corp.wallet_journal(earliest_id)


### Amount per planet.
today = date.today()
print " === INCOME PER PLANET === \n"
sorted_planet_dict = sorted(amount_per_planet.items(), key=lambda x: x[1])
for key,value in reversed(sorted_planet_dict):
	days_active = (today - earliest_time_per_planet[key].date()).days
	isk_per_day = value
	if days_active != 0:
		isk_per_day = value / days_active
	print key, "{:,}".format(value), " ISK per day: ", "{:,}".format(isk_per_day), " (", days_active, ")"

### Amount per system.
print "\n"
print " === INCOME PER SYSTEM === \n"
sorted_dict = sorted(amount_per_system.items(), key=lambda x: x[1])
for key,value in reversed(sorted_dict):
	days_active = (today - earliest_time_per_system[key].date()).days
	isk_per_day = value
	if days_active != 0:
		isk_per_day = value / days_active
	print key, "{:,}".format(value), " POCOS in system", pocos_per_system[key], " ISK per day: ", "{:,}".format(isk_per_day), " (", days_active, ")"

