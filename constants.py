
# These are used to figure out what amount something needs
# to be scaled when importing or exporting.
# These scales are based on the JmsModel's base scale. Which is 100x Halo.
SCALE_MULTIPLIERS = {
	# One foot is 30.48cm. 1 Jms unit is 1/10 of a foot.
	'METRIC'   : 3.048,
	# Halo models in 3dsmax are 1:1 to Jms
	'MAX'      : 1.0,
	# Jms models have 100x the scaling of internal Halo models.
	'HALO'     : 0.01,
}
