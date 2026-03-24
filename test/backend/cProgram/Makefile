all:
	$(MAKE) -f Makefile.main01 all
	$(MAKE) -f Makefile.main02 all

main01Build:
	$(MAKE) -f Makefile.main01 all

main02Build:
	$(MAKE) -f Makefile.main02 all


main01Run:
	$(MAKE) -f Makefile.main01 run

main02Run:
	$(MAKE) -f Makefile.main02 run

clean:
	$(MAKE) -f Makefile.main01 clean
	$(MAKE) -f Makefile.main02 clean

fclean:
	$(MAKE) -f Makefile.main01 fclean
	$(MAKE) -f Makefile.main02 fclean

re: fclean all

.PHONY: all main01Build main01Run main02Build main02Run clean fclean re
