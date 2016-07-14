import argparse
import csv
import datetime
import sys

import dateparser

def main():
	parser = addArgs()
	args = parser.parse_args()

	try:
		#open the file
		filename = args.input
		if args.verbose:
			print("Opening file {0}".format(filename))
		with open(filename) as f:
			freader = csv.reader(f)

			#read the header
			if not args.noheader:
				header = next(freader)
				header = ["ICN","StartDate","EndDate", "Days"] + header
			lineCounter = 0
			rows = []

			#assign the split mode
			if args.day:
				mode = 'd'
			elif args.year:
				mode = 'y'
			elif args.week:
				mode = 'w'
			else:
				mode = 'm'
			if args.verbose:
				print("Split mode: {0}".format(mode))

			#perform the date split
			if args.verbose:
				print("Starting date split.")
			for row in freader:
				if args.verbose: 
					print("Splitting record {0}".format(lineCounter+1))
				rows += (splitLine(row, 
					args.start-1, args.end-1, 
					lineCounter, idCol=args.id-1, 
					verbose=args.verbose, mode=mode))
				lineCounter += 1
			if args.verbose:
				print("Date split complete.")
				if args.export:
					print("Exporting to {0}".format(args.export))
				else:
					print("No export specified. Default: ./splitDateResult.csv")
			
			#export the results
			export = args.export
			if not export:
				export = "./splitDateResult.csv"

			with open(export, 'w', newline='\n') as destfile:
				csvwriter = csv.writer(destfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
				if not args.noheader:
					csvwriter.writerow(header)
				for row in rows:
					csvwriter.writerow(row)

	except OSError as err:
		print("OS error: {0}".format(err))


def splitLine(row, startCol, endCol, lineCounter=0, idCol=0, verbose=False, mode='m'):
	"""Return a list of the original line broken across months

	Arguments
	row 		-- the original csv row
	startCol 	-- integer column number of the starting date (0-indexed)
	endCol 		-- integer column number of the ending date (0-indexed)
	lineCounter	-- integer row number
	idCol 		-- integer column number of the line identifier (0-indexed)
	verbose		-- print additional output?
	mode 		-- d | m | y to split by day, month, or year
	""" 
	try:
		#get the id
		id = ""
		if idCol >= 0:
			id = row[idCol]
			if verbose:
				print("Splitting id {0}".format(id))
		else:
			id = lineCounter
			if verbose:
				print("Splitting line {0}".format(lineCounter))

		startDate = dateparser.parse(row[startCol])
		endDate = dateparser.parse(row[endCol])

		if not startDate or not endDate:
			exit()

		return _breakOutDates(id, startDate, endDate, row, verbose=verbose, mode=mode)

	except ValueError as err:
		print("Value error: {0}".format(err))


def _breakOutDates(id, startDate, endDate, row, verbose=False, mode='m'):
	"""Break out dates and return a list of month sections

	Arguments
	id 			-- unique row identifier
	startDate 	-- first day of entire stay
	endDate 	-- last day of entire stay
	row 		-- row string to append
	verbose 	-- display additional output
	mode		-- d | m | y breaks into days, months, or years
	"""
	#Break out dates
	dateCounter = datetime.datetime(startDate.year, startDate.month, startDate.day)
	subline = 0
	lines = []

	while dateCounter < endDate:
		dateCounter += datetime.timedelta(days=1)
		if ((mode is 'd') 
			or (mode is 'm' 
			and dateCounter.month != startDate.month 
			or dateCounter.year != startDate.year)
			or (mode is 'y' and dateCounter.year != startDate.year)):

			linesToAdd = _formatDateLine(str(id) + "_{0}".format(subline), 
				startDate.date(), (dateCounter - datetime.timedelta(days=1)).date(), row,
				verbose=verbose
				)
			lines.append(linesToAdd)
			startDate = dateCounter
			subline += 1

	#add the final month
	linesToAdd = _formatDateLine(str(id) + "_{0}".format(subline), startDate.date(), 
		endDate.date(),	row, verbose=verbose)
	lines.append(linesToAdd)

	return lines


def _formatDateLine(ID, startDate, endDate, original, verbose=False):
	"""Format the line and return the line string.

	Arguments
	ID 			-- identifier for this row
	startDate 	-- starting date for this row
	endDate 	-- ending date for this row
	original 	-- original row to append
	verbose		-- print the line to STD (default: false)

	Return 		
	string containing formatted line
	"""
	totalDays = (endDate - startDate).days + 1
	output = [ID, startDate, endDate, totalDays]
	output += original
	if verbose:
		print(output)
	return output


def addArgs():
	"""Assign all arguments for the script"""
	parser = argparse.ArgumentParser(
		description="Split dated CSV into rows defined by a date mode.")
	mode = parser.add_mutually_exclusive_group()
	parser.add_argument("-v", "--verbose",
		help="display additional output",
		action="store_true")
	mode.add_argument("--day", action="store_true",
		help = "split daily")
	mode.add_argument("--week", action="store_true",
		help = "split weekly (not implemented yet!)")
	mode.add_argument("--month", action="store_true",
		help = "split monthly (default!)")
	mode.add_argument("--year", action="store_true",
		help = "split yearly")
	parser.add_argument("-f", "--fiscal", default="12/30",
		help = "define a custom year end (default 12/30)")
	parser.add_argument("--noheader", action="store_true",
		help = "first row of source is not a header")
	parser.add_argument("--nocruft", action="store_true",
		help = "don't append old row (not implemented yet)")
	parser.add_argument("-i", "--id", 
		default=0,
		help="integer column of the account ID (1-indexed)",
		type=int)
	parser.add_argument("-e", "--export",
		default=None,
		help="export to save to (default: none)"
		)
	parser.add_argument("start", 
		help="integer column of the start date (1-indexed)",
		type=int)
	parser.add_argument("end", 
		help="integer column of the end date (1-indexed)",
		type=int)
	parser.add_argument("input",
		help="input file to be broken out")
	return parser


if __name__ == '__main__':
	sys.exit(main())
