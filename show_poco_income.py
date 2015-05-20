import evelink.api
import evelink.eve

from datetime import datetime
from datetime import date

api = evelink.api.API(api_key=(4380231, 'uRizCWbLX9mOtC57RAObJc7k3ZWNVSzFhAZ1cfTn9QVXlJ4pi9O1KVQTTfYWeDfi'))
corp = evelink.corp.Corp(api)
response = corp.wallet_journal()

character_api = evelink.api.API(api_key=(4380229, 'VXKUDqdtLCdq0DJy0ooHjd3kKhdTUG9LgwG05zj8pUC90zWqHphnHo5o70sAeVhJ'))
char = evelink.char.Char(95558994, character_api)
char_wallet = char.wallet_journal()

total_spend = 0

for wallet in char_wallet:
	if isinstance(wallet, list):
		for wallet_entry in wallet:
			isk = wallet_entry["amount"]
			if isk < 0:
				total_spend += isk
print "Total ISK spend: ", "{:,}".format(total_spend)

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

total_pocos = 0
for key,value in pocos_per_system.iteritems():
	total_pocos += value

isk_spend_per_poco = -total_spend / total_pocos
#print total_spend, "/", total_pocos, "{:,}".format(isk_spend_per_poco)

### Amount per planet.
today = date.today()
print " === INCOME PER PLANET === \n"
print "{0:<20} {1:>20} {2:>20} {3:>20} {4:>20}".format("Planet", "Total Income", "Isk Per Day", "Days Active", "Even point (days)")
sorted_planet_dict = sorted(amount_per_planet.items(), key=lambda x: x[1])
for key,value in reversed(sorted_planet_dict):
	days_active = (today - earliest_time_per_planet[key].date()).days
	isk_per_day = value
	if days_active != 0:
		isk_per_day = value / days_active
	get_even_point = (isk_spend_per_poco - value) / isk_per_day
	print "{0:<20} {1:>20} {2:>20} {3:>20} {4:>20}".format(key, "{:,.2f}".format(value), "{:,.2f}".format(isk_per_day), days_active, "%.0f" % get_even_point)

### Amount per system.
print "\n"
print " === INCOME PER SYSTEM === \n"
print "{0:<20} {1:>20} {2:>20} {3:>20} {4:>20} {5:>20}".format("System", "Number of POCOs", "Total Income", "Isk Per Day", "Days Active", "Even point (days)")
sorted_dict = sorted(amount_per_system.items(), key=lambda x: x[1])
for key,value in reversed(sorted_dict):
	days_active = (today - earliest_time_per_system[key].date()).days
	isk_per_day = value
	if days_active != 0:
		isk_per_day = value / days_active
	get_even_point = (isk_spend_per_poco * pocos_per_system[key] - value) / isk_per_day
	print "{0:<20} {1:>20} {2:>20} {3:>20} {4:>20} {5:>20}".format(key, pocos_per_system[key],  "{:,.2f}".format(value), "{:,.2f}".format(isk_per_day), days_active, "%.0f" % get_even_point)


