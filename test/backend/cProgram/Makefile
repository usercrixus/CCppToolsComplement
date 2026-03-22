all:
	$(MAKE) -f Makefile.testCProgram1 all
	$(MAKE) -f Makefile.testCProgram2 all

testCProgram1Build:
	$(MAKE) -f Makefile.testCProgram1 all

testCProgram2Build:
	$(MAKE) -f Makefile.testCProgram2 all


testCProgram1Run:
	$(MAKE) -f Makefile.testCProgram1 run

testCProgram2Run:
	$(MAKE) -f Makefile.testCProgram2 run

clean:
	$(MAKE) -f Makefile.testCProgram1 clean
	$(MAKE) -f Makefile.testCProgram2 clean

fclean:
	$(MAKE) -f Makefile.testCProgram1 fclean
	$(MAKE) -f Makefile.testCProgram2 fclean

re: fclean all

.PHONY: all testCProgram1Build testCProgram1Run testCProgram2Build testCProgram2Run clean fclean re
