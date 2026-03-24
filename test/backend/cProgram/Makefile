all:
	$(MAKE) -f Makefile.main01 all
	$(MAKE) -f Makefile.main02 all
	$(MAKE) -f Makefile.main03 all

main01Build:
	$(MAKE) -f Makefile.main01 all

main02Build:
	$(MAKE) -f Makefile.main02 all

main03Build:
	$(MAKE) -f Makefile.main03 all


main01Run:
	$(MAKE) -f Makefile.main01 run

main02Run:
	$(MAKE) -f Makefile.main02 run

main03Run:
	$(MAKE) -f Makefile.main03 run

clean:
	$(MAKE) -f Makefile.main01 clean
	$(MAKE) -f Makefile.main02 clean
	$(MAKE) -f Makefile.main03 clean

fclean:
	$(MAKE) -f Makefile.main01 fclean
	$(MAKE) -f Makefile.main02 fclean
	$(MAKE) -f Makefile.main03 fclean

re: fclean all

.PHONY: all main01Build main01Run main02Build main02Run main03Build main03Run clean fclean re
