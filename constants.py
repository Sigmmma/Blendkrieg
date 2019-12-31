
# These are used to figure out what amount something needs
# to be scaled when importing or exporting.
SCALE_MULTIPLIERS = {
	# 10       : A world unit is 10 feet.
	# 0.032808 : feet per centimeter
	# 100.0    : centimeters per meter.
	'METRIC'   : 10.0/0.032808/100.0,
	# Halo models in 3dsmax as 100x as big as internally.
	'MAX'      : 100.0,
	# Base scale. Used for straight conversions.
	'HALO'     : 1.0,
}
