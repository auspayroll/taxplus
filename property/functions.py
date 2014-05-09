from property.models import *

def getNextPlotId():
	if Property.objects.count() == 0:
		return "PM0000000001"
	else:
		last_plot_id = Property.objects.order_by("-id")[0].plot_id
		plot_id_digit_part = int(last_plot_id[2:]) + 1
		plot_id_digit_part = str(plot_id_digit_part)
		zeros = ''
		for i in range(10-len(plot_id_digit_part)):
			zeros = zeros + '0'
		return 'PM' + zeros + plot_id_digit_part