#!/usr/bin/env python

import names
import argparse 
import random

def phn():
	n = '0000000000'
	while '9' in n[3:6] or n[3:6]=='000' or n[6]==n[7]==n[8]==n[9]:
		n = str(random.randint(10**9, 10**10-1))
	return n[:3]+ n[3:6] +n[6:]

def init(base):
	people = {}
	people['dn'] = 'ou=people,' + base
	people['objectClass'] = 'organizationalUnit'
	people['ou'] = 'people'
	people['leafs'] = {}

	groups = {}
	groups['dn'] = 'ou=groups,' + base
	groups['objectClass'] = 'organizationalUnit'
	groups['ou'] = 'groups'
	groups['leafs'] = {}

	tree = {}
	tree['dn'] = base
	tree['objectClass'] = 'domain'
	tree['leafs'] = {}
	tree['leafs']['people'] = people
	tree['leafs']['groups'] = groups
	return tree

def genrate_tree(tree, n, base, output_file):
	# %80 users, %20 groups
	u_n = int (n*0.8)
	g_n = int (n*0.2)
	
	while u_n > 0:
		rand = genrate_random_person(base)
		# Ensure unique person
		while rand['uid'] in tree['leafs']['people']['leafs']:
			rand = genrate_random_person(base)
		tree['leafs']['people']['leafs'][rand['uid']] = rand
		u_n = u_n - 1 
	u_n = int (n*0.8)
	while g_n > 0:
		rand = genrate_random_group(tree, u_n, base)
		# Ensure unique group 
		while rand['cn'] in tree['leafs']['groups']['leafs']:
			rand = genrate_random_group(tree, u_n, base)
		tree['leafs']['groups']['leafs'][rand['cn']] = rand
		g_n = g_n - 1 
	fd = open(output_file, 'w')
	print_t(tree, fd)
	fd.close()

def genrate_random_person(base):
	name = names.get_full_name().split(' ')
	rand = {}
	rand['dn'] = 'uid=' + '_'.join(name) + ',ou=people,' + base
	rand['objectClass'] = 'inetOrgPerson'
	rand['uid'] = '_'.join(name)
	rand['cn'] = '_'.join(name)
	rand['displayName'] = ' '.join(name)
	rand['givenName'] = name[0]
	rand['sn'] = name[1]
	rand['telephoneNumber'] = phn()
	return rand
	
def genrate_random_group(tree, u_n, base):
	# Pick Random Number between 0 and total entries for group name
	name = 'group' + str(random.randint(0,int(u_n*10/8)))
	rand = {}
	rand['dn'] = 'cn=' + name + ',ou=groups,' + base
	rand['objectClass'] = 'groupOfNames'
	rand['cn'] = name 
	rand['member'] = []

	total_memberships = int (u_n*random.random())
	if total_memberships == 0:
		total_memberships = 1
	all_people = tree['leafs']['people']['leafs'].keys()
	all_people_len = len(all_people)
	while total_memberships > 0:
		index = random.randint(0, all_people_len -1)
		member = tree['leafs']['people']['leafs'][all_people[index]]['dn']
		# No duplicates
		while member in rand['member']:
			index = random.randint(0, all_people_len -1)
			member = tree['leafs']['people']['leafs'][all_people[index]]['dn']
		rand['member'].append(member)
		total_memberships = total_memberships-1
		
	return rand
	
def print_t(tree,fd):
	# dn and leafs is special, dn must print first
	if 'dn' in tree:
		fd.write('dn: ' + tree['dn'] + '\n')
		for attr, val in tree.items():
			if attr == 'dn' or attr == 'leafs':
				continue
			if isinstance(val, list):
				# Multi-Valued Attribute
				for entry in val:
					fd.write(attr+ ': ' + entry+'\n')	
			else: 
				# Single Valued 
				fd.write(attr + ': ' + val + '\n')
		fd.write('\n')
		if 'leafs' in tree:
			print_t(tree['leafs'], fd)
	else: 
		# Print people first to properly create memberOf attr
		if 'people' in tree:
			print_t(tree['people'],fd)
			tree.pop('people')
		if 'groups' in tree:
			print_t(tree['groups'],fd)
			tree.pop('groups')	
		for entry in tree:
			print_t(tree[entry], fd)	

def parse():
	parser = argparse.ArgumentParser("Generate a large amount of random entries (people & groups) for ldap")
	parser.add_argument("-b", "--base_ou", metavar="BASE_OU", help="The base dn where the people and groups ou will be created", required=True)
	parser.add_argument("-o", "--output_ldif", metavar="OUTPUT", help="Path for output ldif file", required=True)
	parser.add_argument("-n", "--number_of_entries", metavar="NUM", help="Total number of entries", required=True)
	
	args = parser.parse_args()

	genrate_tree(init(args.base_ou), int(args.number_of_entries), args.base_ou, args.output_ldif)

parse()

