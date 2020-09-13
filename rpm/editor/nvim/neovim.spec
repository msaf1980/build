#
# spec file for package neovim
#
# Copyright (c) 2019 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


%{?!python3_pkgversion:%define python3_pkgversion 3}
%if 0%{?rhel}
%define __cmake cmake3
BuildRequires:  cmake3
%else
BuildRequires:  cmake
%endif
%if 0%{?rhel} || 0%{?fedora}
%define vimplugin_dir %{_datadir}/vim/vimfiles
%else
%define vimplugin_dir %{_datadir}/vim/site
%endif
Name:           neovim
Version:        %{vers}
Release:        %{rel}%{?dist}
Summary:        Vim-fork focused on extensibility and agility
License:        Apache-2.0 AND Vim
Group:          Productivity/Text/Editors
URL:            https://neovim.io/
Source0:        %{name}-%{version}.%{rel}.tbz
Source1:        sysinit.vim
Source2:        spec-template
Source3:        suse-spec-template
Source99:       neovim-rpmlintrc
# PATCH-FIX-OPENSUSE neovim.patch mcepl@cepl.eu
Patch0:         neovim.patch
# PATCH-FIX-OPENSUSE neovim-0.1.7-bitop.patch mcepl@cepl.eu build with old Lua with external bit module
Patch1:         neovim-0.1.7-bitop.patch
# fix build issue on ppc64
Patch2:         neovim-0.2.0-gcc-prototype.patch
BuildRequires:  desktop-file-utils
BuildRequires:  fdupes
BuildRequires:  filesystem
BuildRequires:  gcc-c++
BuildRequires:  gettext
BuildRequires:  git-core
BuildRequires:  gperf
BuildRequires:  hicolor-icon-theme
BuildRequires:  libtermkey-devel
BuildRequires:  libtool
BuildRequires:  libuv-devel
BuildRequires:  libvterm-devel >= 0.1
BuildRequires:  make
BuildRequires:  msgpack-devel
BuildRequires:  pkgconfig
BuildRequires:  python-rpm-macros
BuildRequires:  unibilium-devel
BuildRequires:  unzip
BuildRequires:  utf8proc-devel
Requires:       gperf
Requires:       libvterm >= 0.1
# Should be Recommends, but I don't want my life too difficult.
Requires:       xsel
Requires:       xdg-utils

BuildRequires:  luajit-devel
BuildRequires:  lua5.1-lpeg
BuildRequires:  lua5.1-mpack
BuildRequires:  lua5.1-luv-devel
Requires:       lua5.1-luv

%if 0%{?fedora}
BuildRequires:  libnsl2-devel
Requires:       python3-neovim
%define lua_version 5.1
%define lua_archdir %{_libdir}/lua/%{lua_version}
%define lua_noarchdir %{lua_pkgdir}
%define lua_incdir %{_includedir}/lua-%{lua_version}
%endif
%if 0%{?rhel}
BuildRequires:  lua-bit32
BuildRequires:  luajit-devel
BuildRequires:  lua-macros
Requires:       lua-bit32
Requires:       python34-neovim
%endif

%description
Neovim is a refactor - and sometimes redactor - in the tradition of
Vim, which itself derives from Stevie. It is not a rewrite, but a
continuation and extension of Vim. Many rewrites, clones, emulators
and imitators exist; some are very clever, but none are Vim. Neovim
strives to be a superset of Vim, notwithstanding some intentionally
removed misfeatures; excepting those few and carefully-considered
excisions, Neovim is Vim. It is built for users who want the good
parts of Vim, without compromise, and more.

%define vimplugin_dir %{_datadir}/vim/site

%lang_package

%prep
%autosetup -p1 -n %{name}

# Remove __DATE__ and __TIME__.
BUILD_TIME=$(LC_ALL=C date -ur %{_sourcedir}/%{name}.changes +'%{H}:%{M}')
BUILD_DATE=$(LC_ALL=C date -ur %{_sourcedir}/%{name}.changes +'%{b} %{d} %{Y}')
sed -i "s/__TIME__/\"$BUILD_TIME\"/" $(grep -rl '__TIME__')
sed -i "s/__DATE__/\"$BUILD_DATE\"/" $(grep -rl '__DATE__')

%build
mkdir -p build
pushd build
export CFLAGS="%{optflags} -fcommon"
export CXXFLAGS="%{optflags} -fcommon"
%{__cmake} .. -DCMAKE_BUILD_TYPE=RelWithDebInfo \
       -DLIBLUV_INCLUDE_DIR:PATH=%{lua_incdir} \
       -DCMAKE_SKIP_RPATH=ON -DCMAKE_VERBOSE_MAKEFILE=ON \
       -DCMAKE_COLOR_MAKEFILE=OFF \
       -DCMAKE_C_FLAGS_RELWITHDEBINFO="$opts" \
       -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix} \
       -DLIBLUV_LIBRARY=%{lua_archdir}/luv.so
make %{?_smp_mflags} VERBOSE=1

popd

%install
DESTDIR=%{buildroot} make install -C build

# system-wide configuration file
install -D -m 644 -p %{SOURCE1} %{buildroot}%{_sysconfdir}/nvim/sysinit.vim
ln -sf  %{_sysconfdir}/nvim/sysinit.vim %{buildroot}%{_datadir}/nvim/sysinit.vim

%if 0%{?suse_version}
install -p -m 644 %{SOURCE3} %{buildroot}%{_datadir}/nvim/template.spec
%else
install -p -m 644 %{SOURCE2} %{buildroot}%{_datadir}/nvim/template.spec
%endif

desktop-file-install --dir=%{buildroot}%{_datadir}/applications \
    runtime/nvim.desktop
install -d -m0755 %{buildroot}%{_datadir}/pixmaps
install -m0644 runtime/nvim.png %{buildroot}%{_datadir}/pixmaps/nvim.png

# Fix exec bits
find %{buildroot}%{_datadir} \( -name \*.bat -o -name \*.awk \) \
    -print -exec chmod -x '{}' \;

# vim/site directories for plugins shared with vim
mkdir -p %{buildroot}%{vimplugin_dir}/{after,after/syntax,autoload,colors,doc,ftdetect,plugin,syntax}

%fdupes %{buildroot}%{_datadir}/
%find_lang nvim

# We have to have rpath
# https://en.opensuse.org/openSUSE:Packaging_checks
export NO_BRP_CHECK_RPATH=true

# %%if 0%%{?suse_version} >= 1500
# %%check
# make test
# %%endif

%if 0%{?suse_version} && 0%{?suse_version} < 1330
%post
%desktop_database_post
%icon_theme_cache_post
%endif

%if 0%{?suse_version} && 0%{?suse_version} < 1330
%postun
%desktop_database_postun
%icon_theme_cache_postun
%endif


%files -f nvim.lang
%doc BACKERS.md CONTRIBUTING.md README.md
%docdir %{_mandir}
%license LICENSE
%{_bindir}/nvim
%{_mandir}/man*/nvim.*
%dir %{_datadir}/nvim
%{_datadir}/nvim/sysinit.vim
%{_datadir}/nvim/template.spec
%{_datadir}/nvim/runtime/
%{_datadir}/applications/*
%{_datadir}/pixmaps/*
%dir %{_sysconfdir}/nvim
%config(noreplace) %{_sysconfdir}/nvim/sysinit.vim
%dir %{_datadir}/vim
%dir %{vimplugin_dir}
%dir %{vimplugin_dir}/after
%dir %{vimplugin_dir}/after/*
%dir %{vimplugin_dir}/autoload
%dir %{vimplugin_dir}/colors
%dir %{vimplugin_dir}/doc
%dir %{vimplugin_dir}/ftdetect
%dir %{vimplugin_dir}/plugin
%dir %{vimplugin_dir}/syntax

%changelog
* Sat Aug 29 2020 mcepl@cepl.eu
- Update to version 0.5.0~git.1598590106.46e74142a:
  * bump libvterm to 0.1.4
  * spell_load_file: Add missing "goto endFAIL" if spellfile is not readable
  * Disable -Wimplicit-fallthrough for tree_sitter/
  * Disable -Wimplicit-fallthrough for funcs.generated.h
  * vim-patch:8.1.2275: using "seesion" looks like a mistake
  * vim-patch:8.2.1517: cannot easily get the character under the cursor
  * vim-patch:8.2.0423: in some environments a few tests are expected to fail
  * vim-patch:8.1.2364: termwinscroll test is flaky on FreeBSD
  * vim-patch:8.1.2089: do not get a hint that $TEST_FILTER was active
  * vim-patch:8.1.2051: double-click test is a bit flaky
  * vim-patch:8.1.1677: tests get stuck when running into an existing swapfile
  * vim-patch:8.1.1516: time reported for a test measured wrong
  * gen_vimdoc: Allow to keep intermediary output
  * Add FIXMEs
  * Add docs for most vim.lsp methods
  * vim-patch:8.2.1511: putting a string in Visual block mode ignores multi-byte
  * vim-patch:8.2.0814: clang warning for implicit conversion
  * vim-patch:8.2.0607: gcc warns for using uninitialized variable
  * vim-patch:8.1.2267: compiler warning for uninitialized variable
  * vim-patch:8.2.1472: ":argdel" does not work like ":.argdel" as documented
  * vim-patch:8.2.1476: filetype test fails on MS-Windows
  * vim-patch:8.2.1474: /usr/lib/udef/rules.d not recognized as udevrules
  * vim-patch:8.1.1115: cannot build with older C compiler
  * vim-patch:8.2.1471: :const only locks the variable, not the value (#12765)
  * runtime/tex.vim: patch to 2547aa930b59 #12504
  * defaults: sessionoptions+=unix,slash #12760
  * version.c: update [ci skip] (#12662)
  * tui: fix pvs/v728
  * shada: fix pvs/v1004
  * userfunc: fix pvs/v547
  * fixup! mksession: always unix slashes "/" for filepaths
  * ex_docmd: replace #define with enum
  * fixup! vim-patch:68e6560b84f1
  * vim-patch:8.2.1458: .gawk files not recognized
  * vim-patch:8.2.1441: running tests in tiny version gives error for summarize.vim
  * vim-patch:8.2.1438: missing tests for interrupting script execution from debugger
  * vim-patch:8.2.1410: adding compiler plugin requires test change
  * vim-patch:8.2.1409: nmpmrc and php.ini filetypes not recognized
  * vim-patch:8.1.2098: mksession test fails on MS-Windows
  * vim-patch:8.1.2097: :mksession is not sufficiently tested
  * vim-patch:8.2.1386: backslash not removed afer space with space in 'isfname'
  * vim-patch:8.2.1379: curly braces expression ending in " }" does not work
  * vim-patch:8.2.1377: triggering the ATTENTION prompt causes typeahead mess up
  * vim-patch:8.2.1369: MS-Windows: autocommand test sometimes fails
  * vim-patch:8.2.1364: invalid memory access when searching for raw string
  * vim-patch:8.2.1361: error for white space after expression in assignment
  * vim-patch:8.2.1360: stray error for white space after expression
  * vim-patch:8.2.1347: cannot easily get the script ID
  * vim-patch:8.1.2341: not so easy to interrupt a script programatically
  * vim-patch:8.1.1674: script to check a colorscheme can be improved
  * vim-patch:8.1.0573: cannot redefine user command without ! in same script
  * lua: add vim.register_keystroke_callback (#12536)
  * treesitter: allow to force predicate addition
  * treesitter: update docs on predicates
  * treesitter: add predicate negation
  * treesitter: add and test vim-match? predicate
  * treesitter: add contains? predicate
  * treesitter(docs): update and refresh docs
  * treesitter: refactor and use lua regexes
  * fix: runtimepath always updates lua package.path
  * Remove unused function (#12719)
  * man.vim: Add - to 'iskeyword' (#12598)
  * libcall: Use "int" for number argument
  * vim-patch:8.1.0264: backup tests fail when CWD is in /tmp
  * vim-patch:8.1.0255: backup test fails when using shadow directory
  * options: fix 'isident' for Windows
  * vim-patch:8.1.0862: no verbose version of character classes
  * tests/terminal/tui: wait 1ms to avoid data race in FreeBSD
  * vim-patch:8.2.1295: tests 44 and 99 are old style
  * vim-patch:8.2.1292: AIDL filetype not recognized
  * vim-patch:8.1.2340: quickfix test fails under valgrind and asan
  * vim-patch:8.1.1202: always get regexp debugging logs when building with -DDEBUG
  * vim-patch:8.1.0194: possibly use of NULL pointer
  * vim-patch:8.1.0192: executing regexp recursively fails with a crash
  * vim-patch:8.2.1267: MS-Windows: tests may fail due to $PROMPT value
  * vim-patch:8.2.1265: crash with EXITFREE when split() fails
  * vim-patch:8.2.1259: empty group in 'tabline' may cause using an invalid pointer
  * vim-patch:8.2.1004: line numbers below filler lines not always updated
  * vim-patch:8.2.0072: memory test still fails on Cirrus CI
  * vim-patch:8.1.2172: spell highlight is wrong at start of the line
  * vim-patch:8.0.1774: reading very long lines can be slow
  * vim-patch:8.2.1254: MS-Windows: regexp test may fail if 'iskeyword' set wrongly
  * ui: fix problem with sattr_T overflow
  * fs: Ensure FileInfo struct is initialized
  * shada: fix failed assertion on exit (#12692)
  * lua: Use #var instead of deprecated table.getn(var)
  * luacheck: Enforce compatibility with Lua5.1
  * Revert "lsp: Fix text edits with the same start position (#12434)" (#12564)
  * vim-patch:8.2.1252: ":marks" may show '< and '> mixed up
  * terminal: fix terminal attribute overflow
  * script: simplify python version check (#12672)
  * build: remove duplicate empty CONFIGURE_COMMAND (#12676)
  * ci: fix build failure in Travis [skip appveyor] (#12678)
  * typval: fix incompatibility with vim
  * vim-patch:8.1.1570: icon signs not displayed properly in the number column
  * vim-patch:8.1.1564: sign column takes up space
  * vim-patch:8.1.1712: signs in number column cause text to be misaligned
  * vim-patch:8.1.1623: display wrong with signs in narrow number column
  * vim-patch:8.1.1564: sign column takes up space
  * buffer_updates: prefer using ml_add_deleted_len_buf
  * buffer_updates: emit valid old_byte_size
  * man.vim: Simplify man#init to reduce load time (#12482)
  * Fix documentation
  * Make the window `nomodifiable` when it's created
  * LSP: make the hover window nomodifiable
  * eval: improve ex_execute (#12445)
  * build: Fix build failure with CI in FreeBSD
  * lua: Fix crash on unprotected lua errors (#12658)
  * doc: Add documentation for some `vim.lsp.buf` functions (#12552)
  * Fix / improve report messages (#12396)
  * tui.c: augment_terminfo: remove unused colorterm argument (#12602)
  * build: fix a problem with the static library name (#12591)
  * startup: fix stall issue with -D options (#12652)
  * vim-patch:8.2.1222: using valgrind in Vim command started by test doesn't work
  * vim-patch:8.2.1211: removed more than dead code
  * vim-patch:8.2.0539: comparing two NULL list fails
  * vim-patch:8.2.0899: assert_equalfile() does not give a hint about the difference
  * vim-patch:8.2.0893: assert_equalfile() does not take a third argument
  * vim-patch:8.1.0819: a failed assert with a long string is hard to read
  * vim-patch:8.2.0895: :mkspell output does not mention the tree type
  * vim-patch:8.2.0894: :mkspell can take very long if the word count is high
  * vim-patch:8.2.0420: Vim9: cannot interrupt a loop with CTRL-C
  * vim-patch:8.2.1170: cursor off by one with block paste while 'virtualedit' "all"
  * vim-patch:8.2.1169: write NUL past allocated space using corrupted spell file
  * lsp: Add support for call hierarchies (#12556)
  * Prevent `flatten` from taking a null list
  * vim-patch:8.2.0937: asan failure in the flatten() test
  * vim-patch:8.2.0935: flattening a list with existing code is slow
  * Reuse inccommand preview window (fix #11529) (#12612)
  * lua: Add ability to pass tables with __call
  * lua: Add ability to pass lua functions directly to vimL
  * treesitter: add parser on_lines callbacks
  * treesitter: cache the capture hl relation
  * treesitter: update test to show overlapping works
  * treesitter: use change calbacks on redraw
  * treesitter: call bufload before parsing (#12603)
  * doc: Add information about lua function calls (#12574)
  * doc: mention that defer_fn applies schedule_wrap (#12601)
  * lua: add options to highlight.on_yank (#12549)
  * lsp: add optional vertical padding, maximal size to floats (#12444)
  * vim-patch:8.1.0093: non-MS-Windows: Cannot interrupt gdb when program is running
  * vim-patch:8.2.1104: Coverity warnts for possible NULL pointer use
  * vim-patch:8.2.1089: Coverity warns for pointer computation
  * vim-patch:8.2.1095: may use pointer after freeing it
  * vim-patch:8.2.1060: not all elinks files are recognized
  * 'clang/Logic error': use enums to avoid undefined array subscript
  * vim-patch:8.1.1372: when evaluating 'statusline' the current window is unknown
  * vim-patch:8.2.1055: no filetype set for pacman config files
  * removed test file
  * version.c: update [ci skip] (#12581)
  * removed whitespace
  * removed retry
  * clarified the reason for wait
  * replaced sleep with a changed mtime for the test file
  * removed unnecessary feed calls
  * doc: fix scripts and regenerate (#12506)
  * docs: Describe how to escape keycodes with nvim_feedkeys (#12484)
  * Added test
  * Update file on focus gained
  * Added healt check for tmux focus events
  * version.c: update [ci skip] (#12524)
  * lsp: Use nvim_buf_get_lines in locations_to_items and add more tests (#12357)
  * treesitter: use single nodes in set_ranges
  * treesitter: separate tests into smaller pieces
  * treesitter: fix lint
  * treesitter: use nodes to mark ranges
  * treesitter: add some documentation for parsers
  * treesitter: fix some clint errors
  * treesitter: test newly added set_included_ranges
  * treesitter: add set_included_ranges to the parser
  * doc: fix wordcount description
  * LSP: Set current name as default rename text (#12553)
  * vim-patch:8.2.1044: not all systemd file types are recognized (#12527)
  * vim-patch:8.2.0865 syntax: Add command to control how foldlevel is computed
  * vim-patch:8.2.1041: test summary is missing executed count (#12519)
  * lsp: when apply text edits, set buflisted on buffers (#12489)
  * syntax: Factor out duplicate E390 strings
  * syntax: factor out helper to compute the syntax-based foldlevel
  * treesitter: simplify puhstree call process
  * terminal: preserve mode when using <Cmd>wincmd in terminal mode (#12254)
  * main.c: fix hang issue with recoverymode (#12496)
  * eval: fix assertion failure in garbage collection (#12436)
  * lsp: Add sync variant of LSP formatting
  * version.c: update [ci skip] (#12391)
  * neovim-qt: bump to version 0.2.16 (#12508)
  * vim-patch:8.2.0999: moving to next sentence gets stuck on quote
  * vim-patch:8.2.0998: not all tag code is tested
  * vim-patch:8.2.0983: SConstruct file type not recognized
  * vim-patch:8.2.0980: raku file extension not recognized
  * vim-patch:8.2.0964: TextYankPost does not provide info about Visual selection
  * vim-patch:8.2.0963: number increment/decrement does not work with 'virtualedit'
  * vim-patch:8.2.0966: 'shortmess' flag "n" not used in two places
  * vim-patch:8.2.0954: not all desktop files are recognized
  * vim-patch:8.1.1977: terminal debugger plugin may hang
  * vim-patch:8.2.0938: NFA regexp uses tolower ()to compare ignore-case
  * option: fix pvs/v547
  * eval: fix pvs/v547
  * vim-patch:8.2.0932: missspelling spelllang
  * vim-patch:8.2.0930: script filetype detection trips over env -S argument
  * vim-patch:8.2.0927: some sshconfig and ssdhconfig files are not recognized
  * vim-patch:8.0.1554: custom plugins loaded with --clean
  * lsp: Add new highlight groups used in show_line_diagnostics (#12473)
  * tex.vim: patch runtime/indent to 388a5d4f20b4
  * tex.vim: patch runtime to 65e0d77a66b7
  * tex.vim: patch runtime to 388a5d4f20b4
  * tex.vim: patch runtime to 1d9215b9aaa1
  * doc: fix vim.api.nvim_buf_attach callback arguments
  * Fix highlight group names in LSP documentation (#12427)
  * lsp: Fix text edits with the same start position (#12434)
  * man.vim: Remove unnecessary code
  * man.vim: Fix tagfunc to respect b:man_default_sects
  * man.vim: Refactor verify_exists to unset $MANSECT as needed
  * lsp: Add `BufLeave` to `close_preview_autocmd` function call (#12477)
  * test: Fix ignored LSP tests (#12470)
  * lsp: Fix #12449 textDocumentSync.save can be boolean. Access textDocumentSync.save.includeText only if table. (#12450)
  * lsp: even if contents before change is 0 byte, request to server
  * issue template: fix label syntax for lsp bug report
  * add GitHub issue template for lsp
  * Add overlapped option to jobstart
  * vim-patch:8.2.0920: writing viminfo fails with a circular reference
  * shada: fix write E5004 error on exit
  * vim-patch:8.2.0629: setting a boolean option to v:false does not work
  * vim-patch:8.2.0111: VAR_SPECIAL is also used for booleans
  * test: remove flaky unhelpful test
  * ci: bump openbsd image 6.5 -> 6.7
  * vim-patch:8.2.0905: test coverage could be better
  * vim-patch:8.2.0892: ubsan warns for undefined behavior
  * vim-patch:8.1.2335: error message for function arguments may use NULL pointer
  * vim-patch:8.2.0491: cannot recognize a <script> mapping using maparg()
  * vim-patch:8.2.0873: a .jl file can be sawfish (lisp) or Julia
  * vim-patch:8.1.2018: using freed memory when out of memory and displaying message
  * vim-patch:8.1.1895: using NULL pointer when out of memory
  * vim-patch:8.0.1564: too many #ifdefs
  * vim-patch:8.1.0917: double free when running out of memory
  * vim-patch:8.2.0089: crash when running out of memory in :setfiletype completion
  * lsp: do not process diagnostics for unloaded buffers (#12440)
  * lsp: compute height of floating preview correctly for wrapped lines (#12380)
  * lsp: Add check for `declaration` and `typeDefinition` support in vim lsp server before making `request` (#12421)
  * lua: fix behavior when split empty string (#12429)
  * build: match WSL2 kernel name (#12425)
  * treesitter: update runtime
  * treesitter: fix tests
  * Add v:event.visual during `TextYankPost` (#12382)
  * lua: fix infinite loop for vim.split on empty string (#12420)
  * treesitter: enhance script and add README
  * treesitter: add update script and update runtime
  * treesitter: update runtime
  * lua: add vim.highlight.range (#12401)
  * vim-patch.sh: fix bash version-check message #12398
  * test: rewrite to multiple arguments
  * runtime: fix remote plugin command fails at some case
  * vim-patch:8.2.0843: filetype elm not detected (#12403)
  * lua: vim.wait implementation
  * lua: vim.wait initial outline
  * provider: Fix ruby checkhealth error for Windows (#12400)
  * API: nvim_create_buf: unset 'modeline' in scratch-buffer #12379
  * lua: simple snippet support in the completion items (#12118)
  * lsp: add preview_location util function (#12368)
  * lsp: make the command error message more detailed (#11633)
  * [squash] fix comment [skip ci]
  * deps: update libuv
  * win/TUI: enable mouse on ConEmu and vtpcon without vti
  * win: use virtual terminal input (VTI) if available #11803
  * eval: fix problem with free_unref_funccal not being called
  * vim-patch:8.1.1485: double free when garbage_collect() is used in autocommand
  * vim-patch:8.1.1484: some tests are slow
  * nvim_input: add test
  * input: fix stack overflow
  * vim-patch:8.0.1668: terminal debugger: can't re-open source code window (#12329)
  * vim-patch:8.1.2233: cannot get the Vim command line arguments (#12117)
  * lsp: change log name to "lsp.log" from "vim-lsp.log"
  * doc: Add optional d for `:lcd` and `:tcd` (#12359)
  * vim-patch:8.2.0810: error when appending "tagfile" to 'wildoptions'
  * vim-patch:8.2.0037: missing renamed message
  * vim-patch:8.2.0036: not enough test coverage for match functions
  * vim-patch:8.1.2228: screenpos() returns wrong values when 'number' is set
  * vim-patch:8.2.0766: display error when using 'number' and 'breakindent'
  * Change uri_to_fname to not convert non-file URIs (#12351)
  * LSP: Don't swallow bufnr argument from callbacks (#12350)
  * fixed hang issue with --headless and -r option specified (#12209)
  * provider: Add python3.9 to autoload/provider/pythonx.vim (#12344)
  * Add tests for jump_to_location
  * Use get_line_byte_from_position in jump_to_location
  * Refactor fetching the line byte
  * lsp: fix get diagnositcs
  * test: fix flaky vim.defer_fn test
  * lua: Add highlight.on_yank (#12279)
  * doc: Vim internal variables & options in lua (#12302)
  * lsp: Fix timezone format of LSP log (ISO 8601) (#12332)
  * lsp: Handle end lines in apply_text_edits (#12314)
  * lua: add tbl_deep_extend (#11969)
  * matchdelete: fix porting (#12328)
  * vim-patch:8.1.1084: cannot delete a match from another window (#12325)
  * Check for nil before checking for empty table
  * LSP: Add textDocument/codeAction support (#11607)
  * LSP: Add workspace.applyEdit client capabilities (#12313)
  * lsp: fix bug when documentEdit version=null for unattached buffer (#12272)
  * vim-patch:8.2.0736: some files not recognized as pamenv
  * vim-patch:8.2.0309: window-local values have confusing name
  * vim-patch:8.2.0308: 'showbreak' does not work for a very long line
  * vim-patch:8.2.0713: the pam_environment file is not recognized
  * vim-patch:8.2.0705: indent tests don't run on CI for FreeBSD
  * vim-patch:8.1.1186: readdir() allocates list twice
  * LSP: Make applyEdit return a response (#12270)
  * test: add more profile tests
  * viml/profile: fix issue where profile is not reset on stop
  * viml/profile: fix use after free
  * runtime/tutor: fix broken inline spans #12282
  * lsp: Make apply_text_edits non-ASCII safe (#12223)
  * lsp: Handle unknown CompletionItemKind and  SymbolKind (#12257)
  * lua: Add buffer, window and tab accessors (#12268)
  * lsp: set buflisted when jumping to location (#12253)
  * vim-patch:8.1.1435: memory usage test is a bit too flaky
  * vim-patch:8.1.1058: memory usage test may still fail on some systems
  * vim-patch:8.1.1037: memory usage test may still fail on some systems
  * vim-patch:8.1.1033: memory usage test may still fail on some systems
  * vim-patch:8.1.1031: memory usage test may still fail
  * vim-patch:8.1.1027: memory usage test sometimes fails
  * vim-patch:8.1.1007: using closure may consume a lot of memory
  * vim-patch:8.1.0475: memory not freed on exit when quit in autocmd
  * vim-patch:8.1.1120: cannot easily get directory entry matches #12222
  * paste: support replace mode (#11945)
  * tag: fix problem when tagfunc return value is v:null (#12251)
  * terminal: disable 'scrolloff' (fixes flicker)
  * terminal: always return zero from get_scrolloff_value() #12230
  * lsp: fix tagstack for location jump #12248
  * LSP: Avoid URI-to-fname conversion for non-file URIs #12243
  * checkhealth/ruby: fix off-by-one error #12245
  * funcs: Fix a memory leak in f_expand (#12227)
  * lsp: add a lsp.util.apply_text_edits test(pending)
  * lsp: fix apply_text_document_edit test
  * vim-patch:8.2.0692: startup test fails on MS-Windows
  * vim-patch:8.2.0691: startup test fails
  * vim-patch:8.2.0688: output clobbered if setting 'verbose' to see shell commands
  * vim-patch:8.2.0681: pattern for 'hlsearch' highlighting may leak
  * vim-patch:8.2.0678: rare crash for popup menu
  * vim-patch:8.2.0663: not all systemd temp files are recognized
  * vim-patch:8.1.0868: crash if triggering garbage collector after a function call
  * vim-patch:8.1.0800: may use a lot of memory when a function refers itself
  * vim-patch:8.1.1581: shared functions for testing are disorganised
  * vim-patch:8.2.0649: undo problem whn an InsertLeave autocommand resets undo
  * vim-patch:8.2.0648: semicolon search does not work in first line
  * lsp: fixup workspace symbol capabilities (#12233)
  * lsp: add workspace/symbol (#12224)
  * LSP: Support LocationLink (#12231)
  * vim-patch:8.1.0816: test for 'runtimepath' in session fails on MS-Windows
  * vim-patch:8.1.0814: :mksession cannot handle a very long 'runtimepath'
  * lsp: add lsp.util.symbols_to_items test
  * lsp: fix lsp.util.symbols_to_items
  * [LSP] check for vim.NIL and add apply_text_document_edit tests
  * version.c: update [ci skip] #12196
  * build: Inherit -n and -jN flags if Ninja #12219
  * doc/UI: mode_info_set: mention colors should be swapped #12211
  * treesitter: unknown predicates always match #12173
  * LSP: enable using different highlighting rules for LSP signs (#12176)
  * lsp/completion: Expose completion_item under completed_items.user_data.
  * vim-patch:8.2.0084: complete item "user_data" can only be a string
  * LSP: support tagstack #12096
  * lsp: use vim.tbl_isempty to check sign (#12190)
  * tui: Fix italics when $TERM is screen in tmux #12199
  * api/ui: simplify popup menu position get/set logic; fix test
  * api/ui: allow set bounds row and col to be less than 0; ui_pum_get_pos: return first extui bounds information instead of reducing
  * gen_api_dispatch.lua: allow msgpack int for Float args; test: add ui_pum_set_bounds and tv_dict_add_float tests
  * external pum: use floating point geometry; typval: add tv_dict_add_float
  * ui_pum_get_pos: return internal pum position if external pum pos not found
  * API/UI: Allow UI to set PUM position and size, and pass the position to CompleteChanged
  * vim-patch:8.0.1375: window size wrong after maximizing with WinBar
  * vim-patch:8.1.1264: crash when closing window from WinBar click
  * vim-patch:8.0.1139: using window toolbar changes state
  * vim-patch:8.0.1334: splitting a window with a WinBar damages window layout
  * vim-patch:8.0.1292: quick clicks in the WinBar start Visual mode
  * vim-patch:8.0.1138: click in window toolbar starts Visual mode
  * vim-patch:8.0.1142: window toolbar menu gets a tear-off item
  * vim-patch:8.0.1125: wrong window height when splitting window with window toolbar
  * vim-patch:8.0.1123: cannot define a toolbar for a window
  * LSP: don't redefine LspDiagnostics signs #12164
  * LSP: Fix show_line_diagnostics #12186
  * lint: use docstring style #12187
  * LSP: Add a check for null version in VersionedTextDocumentIdentifier (#12185)
  * tui: improve support for GNU Screen (#12098)
  * LSP: remove obsolete "peek definition" code #12178
  * TUI: block signals on suspend #12180
  * ci/travis: Enable ipv6 #12182
  * vim-patch:8.2.0638: MS-Windows: messages test fails
  * vim-patch:8.2.0635: when using 256 colors DarkYellow does not show expected color
  * LSP: Expose diagnostics grouped by bufnr (#11932)
  * lsp: remove buffer version on buffer_detach (#12029)
  * version.c: update [ci skip] (#12084)
  * helpers: fix FIXED_TEMP_ARRAY
  * lint: fix linting issues
  * extmark: introduce extmark_splice_cols
  * folds: decrease reliance on global 'curwin'
  * lsp: callback for references now opens qf (#12171)
  * treesitter: check for integer overflow (#12135)
  * vim-patch:8.1.2225: the "last used" info of a buffer is under used
  * terminal: Fix mouse coordinates issue (#12158)
  * lsp: do not assert even if the code does not exist in ErrorCodes (#11981)
  * lsp: textDocument/definition can return Location or Location[] (#12014)
  * doc: fix vim.lsp.stop_all_clients doc (#12055)
  * Test on actual libuv version number, not on existence of symbol.
  * Make neovim building even with libuv 1.18.0
  * vim-patch:8.0.1651: cannot filter :ls output for terminal buffers
  * vim-patch:7.4.1988
  * Apply suggestions from code review
  * Check for bash version in vim-patch.sh
  * mark userfunc as legacy
  * rename: user_funcs -> userfunc
  * fix: includes
  * fix: moved macros
  * fix: moved some static inline function
  * fix: vvlua_partial
  * fix: made eval_lavars_used global
  * fix: include static function declarations
  * fix: header updates
  * Removed redundant define
  * fix: factor out make_partial
  * fix: prof functions
  * fix: var_set_global
  * fix: find_var_ht_dict
  * fix: factor out new functions
  * fix: func_init
  * unstatic some functions
  * moved more stuff
  * created header file
  * moved functions to user_funcs.c (no code changes)
  * doc
  * set -u before return
  * scripts/vim-patch.sh: add -m to usage
* Tue Jun  2 2020 Matej Cepl <mcepl@suse.com>
- Enable -fcommon in order to fix gh#neovim/neovim#12423.
* Mon May  4 2020 Matej Cepl <mcepl@suse.com>
- Switch on generating -lang package (or at least an attempt to do so)
* Tue Apr 21 2020 Matej Cepl <mcepl@suse.com>
- Remove libuv-compat.patch, as it has been merged upstream.
* Tue Apr 21 2020 mcepl@cepl.eu
- Update to version 0.5.0~git.1587411079.9678fe4cf:
  * test: add docs for get_completion_word test
  * test: add get_completion_word test for text_doc...
  * tui: Don't call uv_write without output (#12146)
  * LSP/completion: Add completion text helper function
  * lsp: export convert_signature_help_to_markdown_lines (#11950)
  * lua: allow deepcopy of functions (#12136)
  * lsp: replace the event that closes the signature help preview window from InsertCharPre to CursolMovedI (#11954)
  * LSP: fix breakage when severity isn't specified (#12027)
  * treesitter: remove utf8proc dependency
  * treesitter: escape backslashes in queries
  * treesitter: update vendor code
  * vim-patch:8.2.0589: .bsd file type not recognized
  * vim-patch:8.2.0584: viminfo file uses obsolete function file_readable()
  * folds: decrease reliance on global "curwin" (#12132)
  * doc:Fix incorrect nvim config paths in documentation (#12134)
  * lsp: provide a default for missing reference kind (#12127)
  * win,runtime: Fix problem when win32yank was a symbolic link in WSL [skip ci] (#12124)
  * vim-patch:8.2.0575: :digraph! not tested
  * Suppress Microsoft copyright banner. (#12114)
  * Use libnvim as OUTPUT_NAME for libnvim (#12119)
  * TUI: support setting cursor color in tmux (#12100)
  * vim-patch:8.2.0549: user systemd files not recognized
  * vim-patch:8.2.0544: memory leak in search test
  * vim-patch:8.2.0507: getbufvar() may get the wrong dictionary
  * vim-patch:8.2.0473: variables declared in an outer scope
  * vim-patch:8.2.0134: some map functionality not covered by tests
  * vim-patch:8.2.0474: cannot use :write when using a plugin with BufWriteCmd
  * vim-patch:8.2.0464: typos and other small problems
  * vim-patch:8.2.0457: Test_quotestar() often fails when run under valgrind
  * vim-patch:8.1.1745: compiler warning for unused argument
  * vim-patch:8.2.0415: bsdl filetype is not detected
  * vim-patch:8.2.0406: FileReadCmd event not well tested
  * vim-patch:8.1.2282: crash when passing many arguments through a partial
  * vim-patch:8.1.2280: crash when passing partial to substitute()
  * vim-patch:8.2.0398: profile test fails when two functions take same time
  * vim-patch:8.2.0397: delayed screen update when using undo from Insert mode
  * vim-patch:8.2.0041: leaking memory when selecting spell suggestion
  * vim-patch:8.1.2147: crash when allocating memory fails
  * pvs/v502: use explicit ternary in for-loop
  * vim-patch:8.2.0389: delayed redraw when shifting text from Insert mode
  * vim-patch:8.2.0387: error for possible NULL argument to qsort()
  * pvs/v595: check if extmark not NULL
  * pvs/v560: remove redundant line check
  * vim-patch:8.2.0381: using freed memory with :lvimgrep and autocommand
  * vim-patch:8.2.0365: tag kind can't be a multi-byte character
  * vim-patch:8.2.0366: hardcopy command not tested enough
  * vim-patch:8.2.0560: compiler warning in tiny build
  * vim-patch:8.2.0027: still some /* */ comments
  * vim-patch:8.1.2387: using old C style comments
  * vim-patch:8.1.2378: using old C style comments
  * vim-patch:8.1.2366: using old C style comments
  * vim-patch:8.1.2389: using old C style comments
  * Change to canonicalize only when reparse point in included
  * Change resolve() to resolve symbolic links on Windows
  * vim-patch:8.1.1568: strftime() test fails on MS-Windows
  * vim-patch:8.1.1567: localtime_r() does not respond to $TZ changes
  * vim-patch:8.1.1313: warnings for using localtime() and ctime()
  * Fix screen terminal family issues
  * Fix splitting issue on gnu screen
  * LSP/completion: add textEdit support
* Tue Apr 21 2020 Matej Cepl <mcepl@suse.com>
- Update libuv-compat.patch to reflect comments on
  gh#neovim/neovim#12108
* Mon Apr 13 2020 Matej Cepl <mcepl@suse.com>
- Don't use lua-macros for Fedora
* Sun Apr 12 2020 Matej Cepl <mcepl@suse.com>
- Don't define out own lua macros, rely on fixed lua-macros.
* Sat Apr 11 2020 Matej Cepl <mcepl@suse.com>
- Add libuv-compat.patch to allow build on openSUSE Leap 15.* with old
  libuv (1.18.0).
* Sat Apr 11 2020 mcepl@cepl.eu
- Update to version 0.5.0~git.1586361452.1f56f9a4b:
  * netrw.vim: gx should ignore terminal buffers #12091
  * version.c: update [ci skip] #11995
  * api/ui: win_viewport event for visible range and cursor position in window
  * vim-patch.sh: Fix creation of commit list for PR review
  * vim.uri: fix uri_to_fname (#12059)
  * doc: Fix wildmenu doc inconsistencies and typos
  * popupmenu: don't use 'rightleft' option in cmdline mode
  * TUI: do not use "nvim_get_option" in tui thread
  * Install gettext for msgfmt/msgmerge
  * Set FUNCTIONALTEST=functionaltest-lua for s390x
  * Install pynvim with --user to avoid permission issues
  * Add big-endian, s390x job to Travis
  * vim-patch:8.1.0864 Make 'scrolloff' and 'sidescrolloff' options window local (#11854)
  * vim-patch:8.2.0361: internal error when using "0" for a callback
  * vim-patch:8.2.0360: yaml files are only recognized by the file extension
  * vim-patch:8.1.1279: cannot set 'spellang' to "sr@latin"
  * Revert "ci/Appveyor: install diffutils via scoop"
  * diff.c: fix sprintf call
  * lsp: make showMessage and logMessage callbacks different (#11942)
  * updating doc
  * lua: add vim.tbl_len() #11889
  * version.c: update [ci skip] #11721
  * vim-patch:8.1.1793: mixed comment style in globals
  * vim-patch:8.1.1108: test for 'visualbell' doesn't work
  * vim-patch:8.1.1107: no test for 'visualbell'
  * vim-patch:8.2.0108: when sign text is changed a manual redraw is needed
  * vim-patch:8.1.0939: no completion for sign group names
  * vim-patch:8.1.1552: cursor position is wrong after sign column changes
  * vim-patch:8.1.1489: sign order wrong when priority was changed
  * vim-patch:8.1.1466: not updating priority on existing sign
  * vim-patch:8.1.0896: tests for restricted mode no run for MS-Windows GUI
  * vim-patch:8.1.0885: test for restricted hangs on MS-Windows GUI
  * vim-patch:8.1.0881: can execute shell commands in rvim through interfaces
  * vim-patch:8.1.0883: missing some changes for Ex commands
  * vim-patch:8.1.1642: may use uninitialized variable
  * vim-patch:8.1.0253: saving and restoring window title does not always work
  * addressing reviews
  * vim-patch:8.2.0135: bracketed paste can still cause invalid memory access
  * vim-patch:8.2.0133: invalid memory access with search command
  * vim-patch:8.0.1587: inserting from the clipboard doesn't work literally
  * pvs/v1048: variable was assigned same value
  * 'clang/Logic error': zero-init MarkTreeIter vars
  * vim-patch:8.1.1510: a plugin cannot easily expand a command like done internally
  * man.vim: Handle `man` errors when looking for man-paths
  * lsp: add 'textDocument/documentSymbol’ callback
  * vim-patch:8.1.0619: :echomsg and :echoerr do not handle List and Dict
  * win/l10n: add zh-* locale aliases #11963
  * deps: Fix luv-static build issues #11961
  * foldcolumn: allow auto:X
  * lsp: add bufnr to callback function arguments
  * Use buffer version instead of changedtick for edits
  * LSP: Remove diagnostic message handling in locations_to_items
  * LSP/references: Add context to locations returned by server
  * Add signs for Lsp diagnostics (#11668)
  * LSP/hover: Do not throw away contents if first line is empty (#11939)
  * add support to show diagnostics count in statusline (#11641)
  * LSP: implement documentHighlight (#11638)
  * lua: add regex support, and `@match` support in treesitter queries
  * treesitter: redraw on changed query
  * treesitter: update vendored tree-sitter runtime
  * TUI: reset background color before scroll #11909
  * cmake: Check for -fno-common and use it if available
  * nvim: Correctly setup global channels
  * nvim:msgpack: Correctly set up global ch_before_blocking_events
  * nvim: Fix enum declaration of RemapValues
  * nvim:viml: Fix enum declaration of ExprParserFlags
  * nvim:eval: Fix enum declaration for ListLenSpecials
  * clang/scan-build: restore required code
  * CI/travis: workaround broken homebrew
  * PVS/V618: fix printf-style args #11888
  * lsp/completion: show duplicates in completion popup #11920
  * doc: LOG_CALLSTACK: mention "-no-pie" [ci skip]
  * vim-patch:8.1.1122: char2nr() does not handle composing characters
  * vim-patch:8.1.1868: multi-byte chars in 'listchars' fail with 'linebreak' set
  * quickfix.c: Fix vimgrep regression #11907
  * test: always use "set more" with :digraph test
  * clang/scan-build: fix dead stores #11900
  * lsp: make functions private and use filter function
  * lsp: respect the sort order if there is sortText
  * lsp: fix textDocument/completion handling
  * doc: C-Y and C-E in wildmenu completion
  * lua: move test helper function, map and filter, to vim.shared module
  * loop_close: close all handles
  * loop_close: call uv_stop(), fix bug
  * loop_close: timout after 2 seconds #11821
  * test: always dump logs on failure #11886
  * test/LSP: assert contents of log file
  * lsp/rpc.lua: fix `env` application function
  * test/LSP: dump logs on error
  * LSP: fix validate_client_config
  * test/LSP: use less-generic exit code
  * test: style
  * deps: lua-client 0.2.2-1
  * vim-patch:8.2.0267: no check for a following cmd when calling a function fails
  * vim-patch:8.1.0043: ++bad argument of :edit does not work properly
  * vim-patch:8.0.1660: the terminal API "drop" command doesn't support options
  * vim-patch:8.1.1201: output of :command is hard to read
  * vim-patch:8.1.2187: error for bad regexp even though regexp is not used
  * vim-patch:8.2.0241: crash when setting 'buftype' to "quickfix"
  * vim-patch:8.1.2223: cannot see what buffer an ml_get error is for
  * vim-patch:8.1.0786: ml_get error when updating the status line
  * vim-patch:8.1.2259: running tests may leave XfakeHOME behind
  * vim-patch:8.1.2131: MSVC tests fail
  * vim-patch:8.1.2129: using hard coded executable path in test
  * checkhealth: allow 'sudo install' of 'Neovim::Ext' #11874
  * mouse.c: can click on multibyte foldopen/foldclose (#11863)
  * lua: add vim.tbl_extend and vim.deepcopy test
  * lua: if second argument is vim.empty_dict(), vim.tbl_extend uses empty_dict() instead of {}
  * build: Fix MSVC build failure on CI #11865
  * checkhealth: ignore cpamn "!" output #11869
  * clang bug: Dead assignment `ns_id`
  * doc/lsp: start_client config cmd must be a list (#11866)
  * lua: vim.deepcopy uses empty_dict() instead of {} for empty_dict()
  * test: add json_encode test for vim.empty_dict()
  * Fix issue where callbacks are garbage collected
  * vim-patch:8.1.0092: prompt buffer test fails
  * vim-patch:8.1.0091: MS-Windows: Cannot interrupt gdb when program is running
  * vim-patch:8.1.0071: terminal debugger only works with the terminal feature
  * vim-patch:8.1.0070: missing part of the changes for prompt_setinterrupt()
  * vim-patch:8.1.0069: cannot handle pressing CTRL-C in a prompt buffer
  * vim-patch:8.1.0036: not restoring Insert mode if leaving prompt buffer with mouse
  * vim-patch:8.1.0032: BS in prompt buffer starts new line
  * vim-patch:8.1.0027: difficult to make a plugin that feeds a line to a job
  * LSP: rename validate_command to _cmd_parts #11847
  * LSP: Refine formatting tabSize #11834
  * Build tree-sitter out-of-source
  * treesitter: cleanup some luahl stuff
  * treesitter: use internal "decorations" buffer
  * doc/manpage: Remove the extra nvim subdirectory
  * eval.c: factor out eval/funcs.c #11828
  * doc/manpage: reference $VIM instead of /usr/local/share #11840 [ci skip]
  * lsp: Support text edit on inactive buffer (#11843)
  * build: always create build/lib/nvim so the install command doesn't fail
  * vim-patch:8.2.0235: draw error when an empty group is removed from 'statusline'
  * LSP: set InitializeParams.rootPath value #11838
  * build: allow to skip treesitter C parser install
  * tests: bail out on libdir just like $VIMRUNTIME, it cannot be calculated
  * treesitter: add standard &rtp/parser/ search path for parsers
  * build: include tree-sitter-c parser in bundled build
  * env: try find library dir (like /usr[/local]/lib/nvim) and add it to &rtp
  * api: add nvim_get_runtime_file for finding runtime files
  * deps/msvc: gettext 0.20.1
  * doc: Fix {spell,mlang}.txt files text encoding #11814
  * deps: gettext 0.20.1
  * lint
  * refactor: rename mch_exit => os_exit
  * refactor: move various things to os/shell.c
  * checkhealth: fix accidental change [ci skip]
  * checkhealth: avoid irrelevant virtualenv executables
  * checkhealth: cleanup, brevity
  * checkhealth: bin directory is Scripts/ on Windows
  * checkhealth: print -> sys.stdout.write
  * checkhealth: better $VIRTUAL_ENV validation #11781
  * ex_getln.c: wildmenu add cancel and apply ops
* Sun Feb  2 2020 mcepl@cepl.eu
- Update to version 0.5.0~git.1580644257.3051342f9:
  * extmarks: fix crash due to invalid column values in inccommand preview
  * vim-patch:8.1.1269: MS-Windows GUI: multibyte chars with a 0x80 byte do not work
  * vim-patch:8.1.0140: recording into a register has focus events
  * vim-patch:8.2.0161: not recognizing .gv file as dot filetype
  * vim-patch:8.2.0190: detect Kotlin files [ci skip] #11796
- Remove now unnecessary extmark_crash.patch and
  neovim-lua-compatibility.patch
* Sat Feb  1 2020 mcepl@cepl.eu
- Add extmark_crash.patch to fix gh#neovim/neovim#11769.
- Update to version 0.5.0~git.1580453794.14a8b3b98:
  * doc: fix typos [ci skip] #11787
  * vim-patch:8.2.0016: test name used twice, option not restored properly
  * vim-patch:8.2.0014: test69 and test95 are old style
  * Fix shift change callbacks reading bad cursor (#11782)
  * vim-patch:8.2.0177: memory leak in get_tags()
  * vim-patch:8.2.0077: settagstack() cannot truncate at current index
  * vim-patch:8.1.0446: options test fails in the GUI
  * vim-patch:8.1.0445: setting 'term' does not store location for termcap options
  * CONTRIBUTING.md: mention "good first issue" label
  * vim-patch:8.2.0171: fix use of uninitialized buffer #11786
  * options: winhighlight: fix incorrect string equality test
  * LSP: show diagnostic in qf/loclist #11777
  * build/MSVC: fix gettext multibyte issue #11774
  * lint
  * refactor: move session functions to ex_session.c
  * vim-patch:8.2.0158: triggering CompleteDone earlier is not backwards compatible
  * vim-patch:8.2.0152: restoring ctrl_x_mode is not needed
  * mksession: always unix slashes "/" for filepaths
  * cleanup/ex_docmd.c: remove most put_eol() calls
  * lint
  * cleanup/ex_docmd.c: remove most put_line() calls
  * mksession: always write LF "\n" line-endings
  * mksession: avoid ":file …" when restoring non-terminal bufs
  * mksession: simplify generated commands
  * mksession: restore same :term buf in split windows
  * spell: towupper(),towlower() are not called
  * vim-patch:8.1.1144: too strict checking of the 'spellfile' option
  * vim-patch:8.1.1143: may pass weird strings to file name expansion
  * spellfile: set_spell_chartab() is dead code
  * spell_defs: remove enc_utf8 redundant checks
  * spell: remove enc_utf8 dead code
  * spell: zero-init structs to fix garbage ptrs
  * screen: add missing redraws after a message
  * terminal: trim CWD slash #11762
  * terminal: absolute CWD in term:// URI #11289
  * vim-patch:8.1.2171: mouse support not always available #11761
  * shell: "..." instead of "[...]" #11760
  * Remove enc_utf8,has_mbyte dead code
  * vim-patch:8.1.2245: third character of 'listchars' tab shows in wrong place
  * vim-patch:8.2.0147: block Visual mode operators not correct when 'linebreak' set
  * vim-patch:8.2.0146: wrong indent when 'showbreak' and 'breakindent' are set
  * vim-patch:8.2.0141: no swift filetype detection (#11747)
  * Fix f_jobstop() failed loudly
  * vim-patch:8.1.0061: fix resetting, setting 'title' #11733
  * wildmode: fix wildmode=longest,full with pum #11690
  * ci/Appveyor: respect -NoTest param
  * provider/perl: test older versions
  * provider/perl: add latest version health check
  * doc: provider-perl
  * provider/perl: skip tests on Windows
  * provider/perl: add health check
  * provider/perl: simplify detection
  * provider/perl: add basic tests
  * remote plugins: add support for perl hosts
  * ci/Appveyor: install diffutils via scoop
  * ci: install perl provider
  * tabpage: "tabnext #" switches to previous tab #11734
  * shed biking: it's always extmarks, never marks extended
  * tabpage: :tabs indicates previous tabpage's curwin
  * restore old 'termencoding' behavior
  * vim-patch:8.1.2421: test88 is old style
  * fixup! fixup! vim-patch.sh: list related missing Vim patches [ci skip] #11514
  * vim-patch:8.1.2031: cursor position wrong when resizing and using conceal
  * doc: autocmd.txt
  * WinClosed: sort auevents.lua; improve tests
  * autocmd: WinClosed exposes window id as <afile>
  * autocmd: add WinClosed event
  * vim-patch:8.2.0123: complete_info() does not work when CompleteDone is triggered
  * vim-patch:8.1.1139: no test for what is fixed in patch 8.1.0716
  * vim-patch:8.1.0716: get warning message when 'completefunc' returns nothing
  * spell: spell_soundfold_sal() is dead code
  * clang/'Logic error': zero-init struct
  * vim-patch:8.2.0120: virtcol() does not check arguments to be valid
  * vim-patch:8.2.0112: illegal memory access when using 'cindent'
  * Remove termtype option
  * Change to replace stderr with conout
  * Add missing include file
  * Change option name from termwintype to termtype
  * Rename from os_win_conpty.{c,h} to pty_conpty_win.{c,h}
  * Add stdin, stdout replacement functions
  * Change enum to a name that follows naming convention
  * Change to use TriState instead of bool
  * Fix function prototype
  * Minor changes in reviewer's point
  * Move ConPTY resize to os_win_conpty.c
  * Change union name from pty_object to object
  * Change to use ConPTY, if available
  * messages: echo "line1\r\nline2" should not clear line1
  * extmarks/bufhl: reimplement using new marktree data structure
  * api_set_error: include expression with "Failed to evaluate expression" (#11713)
  * version.c: update [ci skip] #11689
  * fillchars: fix display on closed fold
  * Add new marktree data structure for storing marks
  * API: include invalid buffer/window/tabpage in error message (#11712)
  * doc [ci skip] #11656
  * edit.c: Ensure undo sync when emulating <Esc>x #11706
  * defaults: set fillchars "foldsep" to box line #11702
  * vim-patch:8.0.1593: :qall never exits active :terminal #11704
  * vim-patch:8.0.1769: refactor save/restore of viewstate #11701
  * vim-patch.sh: fix for bash 4.3 or older #11700
  * tabpage: disallow go-to-previous in cmdline-win #11692
  * LSP: highlight groups test, doc
  * test: hoist buf_lines()
  * test: just say no to hyper-granularity
  * LSP: differentiate diagnostic underline by severity
  * API: nvim_get_hl_by_id: omit hl instead of returning -1  #11685
  * version.c: update [ci skip] #11636
  * Remove (void) hacks, Mark unused attrs
  * vim-patch:8.2.0099: use of NULL pointer when out of memory
  * third-party: upgrade libvterm to v0.1.3 (#11678)
  * ui_grid_resize: fix resize logic for floating window #11655
  * man.vim: workaround for 'cscopetag' #11679
  * vim-patch:8.1.1309: test for Normal highlight fails on MS-Windows GUI
  * vim-patch:8.1.1308: the Normal highlight is not defined when compiled with GUI
  * vim-patch:8.1.1579: dict and list could be GC'ed while displaying error
  * vim-patch:8.1.0851: feedkeys() with "L" does not work properly
  * vim-patch:8.0.1786: no test for 'termwinkey'
  * vim-patch:8.1.0844: when timer fails test will hang forever
  * vim-patch:8.1.0842: getchar_zero test fails on MS-Windows
  * vim-patch:8.1.0840: getchar(0) never returns a character in the terminal
  * vim-patch:8.0.1817: a timer may change v:count unexpectedly
* Fri Jan  3 2020 mcepl@cepl.eu
- Update to version 0.5.0~git.1578063407.234232ff4:
  * vim-patch:8.1.0974: cannot switch from terminal window to previous tabpage
  * vim-patch:8.1.0972: cannot switch from terminal window to next tabpage
  * LSP: place hover window by vertical space #11657
  * vim-patch:8.2.0079: test still fails on MS-Windows #11663
  * option: restore termencoding (readonly) #11662
  * clipboard: do not close stderr together with stdout (fixup #11617)
  * tabpage: track last-used tabpage #11626
  * build.ps1: add "-NoTests" param #11654
  * API: fix crash on copy_object(kObjectTypeWindow) #11651
  * clipboard: close stdout when copying via xclip #11617
  * doc: mention `*_host_prog` ordering sensitivity #11639
  * lua: metatable for empty dict value
  * vim-patch:8.2.0076: Python 3 unicode test fails on MS-Windows
  * vim-patch:8.2.0075: Python 3 unicode test still sometimes fails
  * vim-patch:8.2.0074: Python 3 unicode test someitmes fails
  * vim-patch:8.2.0070: crash when using Python 3 with "debug" encoding
  * PVS/V618: fix emsgf format specifier #11643
  * vim-patch:8.2.0068: crash when using Python 3 with "utf32" encoding
  * vim-patch:8.1.1346: error for Python exception does not show useful info
  * doc: powershell is 'pwsh' on non-Windows OS
  * ci: set nodejs version for tests outside fold
  * ci: test powershell core on macOS
  * LSP: eliminate lsp.print_debug_info…()
  * LSP: eliminate lsp.stop_all_clients()
  * gen_vimdoc.py: rename `mode` to `target`
  * ci: test powershell core on Linux
  * gen_vimdoc.py: generate LSP docs
  * doc: LSP
  * doc [ci skip]
  * CI: set nodejs version to 10 on main scripts
  * vim-patch:8.2.0063: wrong size argument to vim_snprintf()
  * vim-patch:8.1.1741: cleared/added match highlighting not updated in other window
  * vim-patch:8.1.1739: deleted match highlighting not updated in other window
  * gen_vimdoc.py: sort by name
  * gen_vimdoc.py: better handling of inline (non-block) nodes
  * gen_vimdoc.py: fix deprecated check
  * vim-patch:8.0.1356: using simalt in a GUIEnter autocommand inserts characters
  * vim-patch:8.1.2377: GUI: when losing focus a pending operator is executed
  * vim-patch:8.1.1300: in a terminal 'ballooneval' does not work right away
  * ui: add basic tests for pumheight,pumwidth
  * vim-patch:8.2.0058: running tests changes ~/.viminfo
  * vim-patch:8.1.2087: cannot easily select one test function to execute
  * vim-patch:8.1.1875: cannot get size and position of the popup menu
  * vim-patch:8.0.1540: popup menu positioning fails with longer string
  * fixup! vim-patch.sh: list related missing Vim patches [ci skip] #11514
  * vim-patch:8.1.1303: not possible to hide a balloon
  * screen: fix pvs/v1048
  * vim-patch:8.1.0554: popup menu overlaps with preview window
  * vim-patch:8.0.1538: popupmenu is too far left when completion is long
  * vim-patch:8.0.1522: popup menu is positioned in the wrong place
  * vim-patch:8.1.0670: macro for popup menu width is unused
  * vim-patch:8.0.1495: having 'pumwidth' default to zero has no merit
  * vim-patch:8.0.1491: the minimum width of the popup menu is hard coded
  * Revert "runtime: Add vim.lsp.get_client_by_name" #11623
  * netrw.vim: do not save +/* registers p.2 #11625
  * runtime: Add vim.lsp.get_client_by_name (#11603)
  * doc: update 'cpoptions' default value #11619
  * LSP: Fix flaky test #11618
  * os/env: fix pvs/v781
  * misc1: fix pvs/v781
  * ex_getln: fix pvs/v781
  * ex_docmd: fix pvs/v781
  * ex_cmds: fix pvs/v781
  * search: fix pvs/v1048
  * quickfix:  qf_parse_fmt_plus never fails
  * hardcopy: fix pvs/v1048
  * api/vim: fix pvs/v1048
  * clang/'Dead store': remove dead code
  * clang/'Logic error': set ret_tv if non-null
  * fillchars: adding foldopen, foldsep, foldclose
  * Fix scripts/vim-patch.sh for Bash 4.3
  * LSP: Handle rpc RequestCancelled specifically. (#11606)
  * vim-patch.sh: list related missing Vim patches [ci skip] #11514
  * system(), jobstart(): raise error on non-executable #11234
  * snap: set "classic" confinement #11601
  * version.c: update [ci skip] #11600
  * vim-patch:8.2.0033: make_extmatch() OOM #11602
  * gen_vimdoc.py: lint #11593
  * snap: set "strict" confinement #11596
  * spellfile: fix pvs/v1048
  * getchar: fix pvs/v1048
  * charset: fix pvs/v1048
  * tag: fix pvs/v1048
  * eval: fix pvs/V1048
  * vim-patch:8.2.0030: "gF" does not work on output of "verbose command"
  * vim-patch:8.0.1767: with 'incsearch' text may jump up and down
  * tree-sitter: implement query functionality and highlighting prototype [skip.lint]
  * tree-sitter: fix prototypes (to be upstreamed)
  * tree-sitter: fix relative paths in unicode/ subdir
  * tests: ex_terminal_spec: retry ":terminal (with fake shell)" (#11588)
  * tree-sitter: update vendored tree-sitter runtime
  * gen_vimdoc.py: rename for clarity
  * gen_vimdoc.py: mpack: collect functions in 1 dict
  * gen_vimdoc.py: fix "seealso", "xrefs"
  * gen_vimdoc.py: mpack: exclude deprecated functions
  * gen_vimdoc.py: fix mpack generator
  * gen_vimdoc.py: DRY
  * termdebug.vim: Comment out Winbar related things #11552
  * tests: sync Test_undojoin_redo from Vim #11589
  * vim-patch:8.2.0025: repeated word in comment (#11586)
  * LSP: Use async completion for omnifunc. (#11578)
  * build: DownloadAndExtractFile.cmake: retry status_code=7 #11582
  * vim-patch:8.2.0024: filetype Rego not recognized
  * vim-patch:8.2.0019: cannot number of lines of another buffer
  * LSP: Improve the display of the default hover callback. (#11576)
  * LSP: fix omnifunc findstart (#11522)
  * TUI: can make the cursor transparent #11519
  * test/old: skip Test_screenpos for now
  * vim-patch:8.2.0018: :join does not add white space where it should
  * vim-patch:8.2.0015: not all modeline variants are tested
  * fileio: use uint64_t for temp_count #11555
  * vim-patch:8.2.0013: not using a typedef for condstack
  * vim-patch:8.2.0012: some undo functionality is not tested
  * vim-patch:8.2.0010: test64 is old style
  * vim-patch:8.2.0008: test72 is old style
  * vim-patch:8.2.0002: "dj" only deletes first line of closed fold
  * Add support for the pum_getpos() API (#11562)
  * libcallnr: Use int, not int64_t, as the return type for Vim compat
  * Add negative test for type of job's env option
  * snap: allow job failure
  * version.c: update [ci skip] #11415
  * os_getenvname_at_index: Handle Windows env vars whose name starts with =
  * Add os_getfullenv_size/os_copyfullenv
  * jobstart now supports env/clear_env
  * test: new test for setting environment
  * snap: re-enable CI job
  * PVS/V1049: fix numerous "DEFINE_FUNC_ATTRIBUTES" warnings #11544
  * jumplist: browser-style (or 'tagstack') navigation #11530
  * netrw.vim: do not save +/* registers
  * doc: LSP [ci skip] #11524
  * vim-patch:8.1.2408: syntax menu and build instructions outdated
  * vim-patch:8.1.2402: typos and other small things
  * LSP: Add jump when calling gotodef (#11521)
  * Fix access on vim.wo (#11517)
  * runtime/syntax/vim.vim: highlight "blend" keyword #11520
  * vim-patch:8.1.2385: open cmdline window with feedkeys() #11516
  * vim-patch:8.1.2384: test 48 is old style #11509
  * test: always pass a string to expect_msg_seq
  * defaults: set nostartofline
  * API: rename nvim_execute_lua => nvim_exec_lua
  * API: deprecate nvim_command_output
  * log_init: call log_path_init (#11501)
  * testdir/runnvim.sh: create messages file always (#11503)
  * oldtest: support for running by filename (#11473)
  * build: CMakeLists: do not set MIN_LOG_LEVEL with C flags (#11498)
  * src/nvim/testdir/test_quickfix.vim: align with Vim (#11502)
  * dictwatcher: fix use-after-free #11495
  * API: rename nvim_source => nvim_exec
  * API: nvim_source_output
  * API: nvim_source: fix multiline input
  * API: nvim_source: save/restore script context #11159
  * API: nvim_source
  * Add vim.startswith and vim.endswith (#11248)
  * Add vim.cmd as an alias for nvim_command (#11446)
  * Return nil instead of NIL for vim.env (#11486)
  * screen.lua: remove screen:_on_event #11488
  * ci: SourceHut: revisit OpenBSD/FreeBSD config
  * terminfo_is_bsd_console: fallback to false
  * vim-patch:8.1.2367: registers are not sufficiently tested (#11489)
  * snap: disable job until we are approved
  * vim-patch:8.1.2363: ml_get error when accessing Visual area in 'statusline'
  * doc: mention OS pseudo-features in :h feature-list
  * vim-patch:8.1.2355: test with "man" fails on FreeBSD
  * floatwin: show error if window is closed immediately #11476
  * snap: declare "devmode" instead of "classic" #11482
  * vim-patch:8.1.2315: switchbuf=uselast #11480
  * vim-patch:8.1.2017: cannot execute commands after closing cmdline window #11479
  * snap: fix line continuation #11475
  * snap: disable job
  * win_line: Fix crash with 'rightleft' in :terminal #11460
  * deps: update libtermkey to 0.22 #11429
  * snap: more yak-shaving
  * snap: add snapcraft secrets to CI
  * snap: add desktop file, icon
  * snap: add "snap" job to Travis CI
  * snap: fix/update snap builds
  * man.vim: remove K mapping #11472
  * lsp: allow the user to config LspDiagnosticError etc by standard means
  * runtime: russian-jcukenwintype.vim keymap #11461
  * doc: fix typos
  * man.vim: Improve ft=man 'iskeyword' #11457
  * vim-patch:8.1.1268: map completion test fails in GUI
  * vim-patch:8.1.1254: mapping completion contains dead code
  * vim-patch:8.1.1253: mapping completion test fails
  * vim-patch:8.1.1252: not all mapping completion is tested
  * vim-patch:8.1.2349: :lockvar and :unlockvar cannot be followed by "| endif"
  * vim-patch:8.1.2348: :const cannot be followed by "| endif"
  * vim-patch:8.1.2345: .cjs files are not recognized as Javascript
  * options: make 'fillchars' and 'listchars' global-local
  * lua: make vim.wo and vim.bo used nested indexing for specified handle
  * cmake: enable exporting symbols from static libs again
  * LSP: Move default buf callbacks to vim.lsp.callbacks (#11452)
  * UI: emit mouse_on/mouse_off on attach #11455
  * [RFC] extmark: fix E315 in nvim_buf_set_extmark (#11449)
  * doc + extmarks tweaks #11421
  * vim-patch:8.1.0836: user completion test can fail on MS-Windows
  * vim-patch:8.1.0223: completing shell command finds sub-directories in $PATH
  * vim-patch:8.1.1732: completion in cmdwin does not work for buffer-local commands
  * vim-patch:8.1.0461: quickfix: change comment style #11453
  * release.sh [ci skip]
  * man.vim: Update maintainer email
  * man.vim: Hard wrap by default
  * man.vim: Document how to disable bold highlighting
  * man.vim: Ensure 'modifiable' in man#init_pager #11450
  * Bring vim into local scope
  * Add support for textDocument/references.
  * Lua: vim.env, vim.{g,v,w,bo,wo} #11442
  * vim-patch:8.1.1334: respect shortmess=F when buffer is hidden #11443
  * UI tweaks.
  * vim-patch:8.1.0471: some tests are flaky or fail on some systems
  * tests: remove irrelevant timing info
  * test was wrong
  * refactor: use inserted_bytes pattern from vim
  * bufhl: use extmark column adjustment for bufhl
  * vim-patch:8.1.1951: mouse double click test is a bit flaky
  * vim-patch:8.1.2330: vi' does not always work when 'selection' is exclusive
  * vim-patch:8.1.2329: mouse multiple click test is a bit flaky
  * vim-patch:8.1.2183: running a test is a bit verbose
  * vim-patch:8.1.1490: when a single test fails the exit code is not set
  * vim-patch:8.1.0723: cannot easily run specific test when in src/testdir
  * vim-patch:8.1.2269: tags file with very long line stops using binary search
  * vim-patch:8.1.1235: compiler warnings for using STRLEN() value
  * Clear 'cc' in nvim_open_win 'minimal' style #11361 (#11427)
  * Improve the character_offset code.
  * Improve performance of util.set_lines + bugfix
  * Fix encoding translation in other places.
  * Remove comments.
  * Fix position params for encoding.
  * Account for character length in jump position.
  * lualint
  * Fix hovers staying on bufhidden
  * Updates
  * Fix terminal close error message formatting
  * lsp: transmit "\n" after last line when 'eol' is set
  * Remove resolve_bufnr/lualint
  * Use the apply_text_edits from util.
  * Fix reference in rename.
  * Add full text_edit implementation.
  * Extend list_extend to take start/finish.
  * Use err_message in default_callbacks
  * Satisfy lualint.
  * Fix rename support.
  * Spaces not tabs.
  * Change error writer to not be annoying.
  * Change callback resolution to be dynamic.
  * Move everything to buf & default_callbacks
  * Add everything to lsp.buf and get rid of autoload.
  * Add lsp.buf and hover implementation.
  * Bugfix. Don't use nvim.lua that doesn't exist :)
  * Add vim.uri_to_bufnr
  * Bugfixes.
  * Bugfix for floating_preview
  * Reduce code blocks in markdown previews.
  * vim-patch:8.0.1793: no test for "vim -g"
  * vim-patch:8.0.1449: slow redrawing with DirectX
  * deps: upgrade bundled LuaRocks: 2.4.4 => 3.2.1 (#10292)
  * vim-patch:8.1.0251: support full paths for 'backupdir' #11269
  * version.c: update [ci skip] #11160
  * doc: Lua [ci skip] #11378
  * vim-patch:8.1.2317: no test for spell affix file with flag on suffix
  * vim-patch:8.1.2314: vi' sometimes does not select anything
  * vim-patch:8.1.2312: "line:" field in tags file not used
  * TUI: use stdio names instead of magic numbers #11410
  * build/macOS: set -fno-stack-check for LuaJIT build #11412
  * provider/python: add python3.8 executable (#11402)
  * tutor: change arrows (--->) to symbols ✗ and ✓ #11404
  * vim-patch:8.1.2305: no warning for wrong entry in translations
  * vim-patch:8.1.2289: after :diffsplit closing the window does not disable diff
  * diff: move diff globals to diff.h
  * vim-patch:8.1.1922: in diff mode global operations can be very slow
  * Add v:lua.func() vimL syntax for calling lua
  * extmark: don't crash in RO buffer.
  * undo: delete undo_off global without effect
  * vim-patch:8.1.0992: :normal resets reg_executing() result #11398
  * [scripts/gen_vimdoc.py] Generate better-formatted mpack
  * f_getenv/setenv: Access v_special when v_type is VAR_SPECIAL #11388
  * spell: fix clang logic error
  * quickfix: fix dead assignment
  * vim-patch:8.1.0927: USE_CR is never defined
  * vim-patch:8.1.2293: join adds trailing space when second line is empty
  * Sort man pages by relevance during goto_tag()
  * Don't attempt swapfiles for man pages
  * Remove eventignore - :Man now uses :tag to populate the page
  * Factor out parse_one_cmd()
  * vim-patch:8.1.0266: parsing Ex address range is not a separate function
  * lua LSP client: initial implementation (#11336)
  * extmark: fix spelling of "Extmark"
  * extmark: rename ExtendedMark => Extmark
  * doc [ci skip]
  * vim-patch:8.1.0622: adding quickfix items marks items as valid errors #11373
  * extmark: review changes
  * nsmarks: initial commit
  * namespace: add ns_initialized func
  * api: fix typo in debug function name
  * Lua: mark some functions as "private"
  * fix nvim__buf_stats
  * Lua: Use vim.validate() instead of assert()
  * Lua: vim.validate()
  * Lua: vim.validate()
  * man.vim: remove push_tag and simplify man#open_page
  * man.vim: parse the section from the tag
  * man.vim: `:Man` preserves the tag stack
  * man.vim: use 'tagfunc' instead of remapping
  * man.vim: pull out s:get_paths()
* Mon Nov 11 2019 mcepl@cepl.eu
- Update to version 0.4.3+git.1573418145.b9c9283f7:
  * spellfile.vim: improve error message for missing spellfile
  * tests: vim.rpcnotify test is flaky
  * api: add nvim_buf_get_virtual_text() (#11354)
  * lua: vim.rpcrequest, vim.rpcnotify, vim.NIL
  * test/Screen:expect: replace "{IGNORE}" with "{MATCH:…}"
  * tests: Screen:expect: support "{MATCH:…}"
  * paste: Select-mode, Visual-mode #11360
  * quickfix: fix pvs/v547
  * vim-patch:8.1.0324: off-by-one error in cmdidx check
  * vim-patch:8.1.2272: test may hang at more prompt
  * vim-patch:8.1.2270: "gf" is not tested in Visual mode
  * vim-patch:8.1.2268: spell file flag zero is not recognized
  * vim-patch:8.1.2262: unpack assignment in function not recognized
  * vim-patch:8.1.1091: MS-Windows: cannot use multi-byte chars in environment var
  * vim-patch:8.1.2258: may get hit-enter prompt after entering a number
  * vim-patch:8.1.2244: 'wrapscan' is not used for "gn"
  * build: add shlint target for shellcheck (#11350)
  * vim-patch.sh: multiline printf -> heredoc (#11351)
* Fri Nov  8 2019 mcepl@cepl.eu
- Update to version 0.4.2+git.1573222681.2ba212e8c:
  * vim-patch.sh: add missing argument
* Wed Nov  6 2019 mcepl@cepl.eu
- Update to version 0.4.2+git.1573033773.f79369d42:
  * doc: vim.fn, vim.call(), vim.api [ci skip]
  * doc: file-change-detect [ci skip]
  * Simplify + inline/align comment
  * autocmd: Fix event name casing #11332
  * terminal: add tests for palette color forwarding
  * syntax: zero-init local structs
  * quickfix: fix pvs/v547 error
  * vim-patch:8.1.2236: ml_get error if pattern matches beyond last line
  * test/screen: make snapshot_util() work properly in rgb_cterm mode
  * terminal: preserve support for g:terminal_color_X = "#1234ab"
  * highlight: correctly disable index attribute with combine/blend
  * terminal: enable pass through indexed colors to TUI
  * Simplify split_success logic
  * tui: simplify branching of rgb vs cterm colors
  * vim-patch:8.1.2235: "C" with 'virtualedit' set does not include multi-byte char
  * update_version_stamp.lua: Use NUL on Windows #11323
  * vim-patch:8.1.2231: introduce gM command #11321
  * Minor updates and comment format fixes
  * Document skip_colon_white()
  * Prevent prompts during inccommand previews
  * Prevent :topleft, etc modifying the inccommand preview window
  * Only apply 'icm' substitutions when preview was successfully opened
  * Allow multiple leading colons before and after modifiers for 'inccommand'
  * Factor out skip_colon_white()
  * Remove unnecessary expr in 'icm' test
  * lua/executor.c: use TRY_WRAP
  * termdebug.vim: reset evalFromBalloonExprResult #11309
  * vim-patch:8.1.1256: cannot navigate through errors relative to the cursor
  * vim-patch:8.1.1112: duplicate code in quickfix file
  * vim-patch:8.1.1098: quickfix code duplication
  * vim-patch:8.1.1062: quickfix code is repeated
  * provider/pythonx: don't assume CWD (empty string) is in path #11304
  * vim-patch:8.1.1030: quickfix function arguments are inconsistent
  * vim-patch:8.1.1006: repeated code in quickfix support
  * vim-patch:8.1.0532: cannot distinguish between quickfix and location list
  * vim-patch:8.1.0488: using freed memory in quickfix code
  * vim-patch:8.1.0469: too often indexing in qf_lists[]
  * vim-patch:8.1.0407: quickfix code mixes using the stack and a list pointer
  * vim-patch:8.1.0252: quickfix functions are too long
  * lua: add vim.fn.{func} for direct access to vimL function
  * vim-patch:8.1.2154: quickfix window height wrong when there is a tabline
  * vim-patch:8.1.1245: ":copen 10" sets height in full-height window
  * scripts/lua2dox.lua: Remove class declaration block
  * ci: do not skip before_install on lint job
  * ci: use python3 for flake8
  * vim-patch:8.1.2220: :cfile does not abort like other quickfix commands
  * lint
  * gen_vimdoc.py: dump API docs to msgpack #11296
  * win/dist: nvim-qt v0.2.15 #11295
  * tests: remove some redundant legacy tests #11028
  * build: add -fstack-protector* to linker #11292
  * vim-patch:8.1.2218: "gN" is off by one in Visual mode
  * vim-patch:8.1.2207: "gn" doesn't work quite right
  * vim-patch:8.1.2173: searchit() has too many arguments
  * test/pcall_err(): truncate full paths, omit linenr
  * lua/stdlib: adjust some validation messages #11271
  * vim-patch:8.1.0859: handle multibyte "%%v" in 'errorformat' #11285
  * man.vim: never switch to non-man window #11286
  * ci: simplify tree-sitter-cli install
  * CI/Appveyor: set powershell strict mode
  * CI: bump nodejs to v10.x (LTS)
  * tag: fix pvs/v547 error
  * vim-patch:8.1.0455: checking for empty quickfix stack is not consistent
  * vim-patch:8.1.0438: the ex_make() function is too long
  * vim-patch:8.1.0434: copy_loclist() is too long
  * vim-patch:8.1.0410: the ex_copen() function is too long
  * vim-patch:8.1.0345: cannot get the window id associated with the location list
  * vim-patch:8.1.0288: quickfix code uses cmdidx too often
  * vim-patch:8.1.0014: qf_init_ext() is too long
  * runtime: Use module pattern with vim/shared.lua
  * vim-patch:8.1.1962: leaking memory when using tagfunc()
  * vim-patch:8.1.1228: not possible to process tags with a function
  * Perform HASHTAB_ITER bookkeeping before user-code
  * vim-patch:8.1.2197: ExitPre autocommand may cause accessing freed memory
  * vim-patch:8.1.2190: syntax test fails on Mac
  * vim-patch:8.1.2188: build error for missing define
  * vim-patch:8.1.2185: syntax test fails
  * ci/install.sh: pin treesitter to v0.15.9 #11266
  * vim-patch:8.1.2168: heredoc not skipped in if-block #11265
  * TUI/thread: guard env map from potential race with unibilium #11259
  * build/doc/CI: remove/update quickbuild references #11258
  * ex_echo: fix check for got_int #11225
  * test/functional: retry/Screen: failure instead of error #11173
  * vim-patch:8.1.2180: Error E303 is not useful when 'directory' is empty (#11257)
  * vim-patch:8.1.2182: test42 seen as binary by git diff #11256
  * vim-patch:8.1.2178: accessing uninitialized memory in test
  * vim-patch:8.1.2177: Dart files are not recognized
  * vim-patch:8.1.2175: meson files are not recognized
  * vim-patch:8.1.2151: state test is a bit flaky
  * vim-patch:8.1.2162: popup resize test is flaky
  * vim-patch:8.1.2161: mapping test fails
  * vim-patch:8.1.2152: problems navigating tags file on MacOS Catalina
  * tests: let_spec: enable "multibyte env var to child process" (#11233)
  * build: do not build test fixtures by default (#11230)
  * tests: fix non-controversial misuse of `pending` (#11247)
  * vim-patch:8.1.2140: "gk" and "gj" do not work correctly in number column #11208
  * vim-patch:8.1.2096: too many #ifdefs #11229
  * scripts/vim-patch.sh: lazily update Vim source (#11207)
  * tests: tui_spec: fix waiting for terminal to be ready (#11232)
  * deps: pass LDFLAGS+=-static (#11138)
  * mac: fix "tags file not sorted" bug on Catalina (#11222)
  * vim-patch 8.1.0361: remote user not used for completion
  * scripts/vim-patch.sh -l: display commit subjects
  * tests/ui: completely delete "attr_ignore" feature
  * tests/ui: remove unnecessary screen:detach()
  * tests/ui: cleanup illegitimate usages of "attr_ignore"
  * tests/ui: make screen.lua use "linegrid" representation internally
  * vim-patch:8.1.1729: heredoc with trim not properly handled in function
  * vim-patch:8.1.1723: heredoc assignment has no room for new features
  * vim-patch:8.1.1625: script line numbers are not exactly right
  * vim-patch 8.1.0085: no test for completing user name and language
  * vim-patch 8.1.0084: user name completion does not work on MS-Windows
  * vim-patch:8.1.1585: :let-heredoc does not trim enough
  * vim-patch:8.1.1099: the do_tag() function is too long
  * recovery mode (-r/-L): use headless_mode (#11187)
  * vim-patch:8.1.2125: fnamemodify() fails when repeating :e
  * fnamemodify: fix handling of :r after :e #11165
  * test: "!:&" works with powershell #11201
  * Remove "highbright bold" conversion. Fixes #11190
  * update_version_stamp: redirect stderr on first try, --first-parent #11186
  * doc: update shellquote for powershell #11122
  * third-party: upgrade libvterm to 0.1.2 (#11177)
  * ci: AppVeyor: coverage for Lua (Windows) (#10426)
  * ci: OpenBSD: enable functionaltest  (#11178)
  * vim-patch:8.1.1588: in :let-heredoc line continuation is recognized
  * vim-patch:8.1.1362: code and data in tests can be hard to read
  * vim-patch:8.1.1356: some text in heredoc assignment ends the text
  * vim-patch:8.1.1354: getting a list of text lines is clumsy
* Mon Oct  7 2019 Matej Cepl <mcepl@suse.com>
- Update lua-compatibility.patch
* Mon Oct  7 2019 mcepl@cepl.eu
- Update to version 0.4.2+git.1570462960.7faa6c41c:
  * cmake: only set LUA_PRG with successful check (#11172)
  * ci: use cluacov for better performance (#11152)
  * Remove dead code
  * vim-patch:8.1.2120: some MB_ macros are more complicated than necessary
  * ci: submit_coverage: run luacov actually (#11169)
  * test/old: add test_fnamemodify.vim (#11168)
  * lint
  * ci: upgrade tree-sitter from 0.15.2 to 0.15.9
  * tests: retry: "wait() evaluates the condition on given interval" (#11155)
  * tests/functional: keep $TMPDIR in env (#11163)
  * vim-patch:8.1.0586: :digraph output is not easy to read
  * vim-patch:8.1.0059: displayed digraph for "ga" wrong with 'encoding' "cp1251"
  * doc: Fix TEST_FILTER example #11158
  * vim-patch:8.1.1371: cannot recover from a swap file #11081
  * version.c: update [ci skip] #10981
  * vim-patch:8.1.2113: ":help expr-!~?" only works after searching
  * Makefile: use `$TMPDIR` below `src/nvim/testdir` (#11153)
  * Fix potential deadlock #11151
  * ci: coverage for Lua (no Windows, using luacov) (#11127)
  * win_line: update `w_last_cursorline` always
  * tests: tui_spec: improve/merge OptionSet/deferred
  * health: provider: skip checks with `g:loaded_X_provider = 0` (#11147)
  * test/old: align with Vim #11096
  * refactor: wrap common plines() usage in plines_win_full() #11141
  * tui: fix handling of bg response after suspend (#11145)
  * tests: unit: NVIM_TEST_TRACE_LEVEL: default to 0 #11144
  * ci: Travis: simplify 32bit build (#11093)
  * vim-patch:8.1.0330: the qf_add_entries() function is too long
  * shell: improve displaying of pulse (#11130)
  * Fix flaky test: tui_spec: increase timeout (#11134)
  * vim-patch:8.1.0315: helpgrep with language doesn't work properly
  * vim-patch:8.1.2103: wrong error message if "termdebugger" is not executable
  * vim-patch:8.1.0230: directly checking 'buftype' value
  * vim-patch:8.1.2095: leaking memory when getting item from dict
  * vim-patch:8.1.2091: double free when memory allocation fails
  * quickfix: fix pvs/v547 errors
  * vim-patch:8.1.2074: test for SafeState autocommand is a bit flaky
  * test: fix screen assertions
  * vim-patch:8.1.1347: fractional scroll position not restored after closing window
  * vim-patch:8.1.1327: unnecessary scroll after horizontal split
  * vim-patch:8.1.0518: Test_window_split_edit_bufnr() fails on AppVeyor
  * vim-patch:8.1.0517: Test_window_split_edit_alternate() fails on AppVeyor
  * vim-patch:8.1.0514: CTRL-W ^ does not work when alternate buffer has no name
  * vim-patch:8.1.1758: count of g$ not used correctly when text is not wrapped
  * vim-patch:8.1.2072: "gk" moves to start of line instead of upwards
  * vim-patch:8.1.0010: efm_to_regpat() is too long
  * patch_terminfo_bugs: TERM=xterm with non-xterm: ignore smglr (#11132)
  * Fix redraw regression with w_p_cole in visual mode
  * Fix/revisit git-describe enhancement (#11124)
  * build: get rid of warnings with `cmake --debug-output` (#11131)
  * tui: improve handle_background_color: short-circuit (#11067)
  * screen: don't crash on invalid grid cells being recomposed
  * third-party: upgrade libluv: 1.30.0-0 => 1.30.1-1 (#11092)
  * provider#pythonx: resolve/expand exe from host var (#11047)
  * bundle: upgrade LuaJIT to latest v2.1 (#10321)
  * build: run git-describe for dev version during build (#11117)
  * cmake: use LibFindMacros for utf8proc (#11114)
  * terminfo_start: keep first flushing of ui buffer (#11118)
  * cmdline: wildmenumode() should be true with wildoptions+=pum
  * tree-sitter: improve and cleanup tests
  * tree-sitter: use "module" pattern in lua source
  * tree-sitter: handle node equality
  * tree-sitter: start docs
  * tree-sitter: use "range" instead of "point_range" consistently in lua API
  * tree-sitter: simplify editing using the new old_byte_size parameter
  * tree-sitter: fix lint, delete "demo" plugin (replaced by functional tests)
  * tree-sitter: improve parser API (shared parser between plugins)
  * tree-sitter: cleanup tree refcounting
  * tree-sitter: inspect language
  * tree-sitter: add some more API
  * tree-sitter: style
  * tree-sitter: use standard luaL_newmetatable and luaL_checkudata pattern
  * tree-sitter: rename tree_sitter => treesitter for consistency
  * tree-sitter: add basic testing on ci
  * tree-sitter: support pre-registration of languages
  * tree-sitter: objectify API
  * tree-sitter: split tree-sitter lua interface from demo code
  * tree-sitter: cleanup build code
  * Create BuildUtf8proc.cmake and FindUtf8proc.cmake
  * tree-sitter: load parsers as .so files
  * tree-sitter: initial tree-sitter support
  * tree-sitter: change vendored tree-sitter to use nvim memory management
  * tree-sitter: vendor tree-sitter runtime
  * vim-patch:8.1.2083: multi-byte chars do not work properly with "%%.*S" in printf() (#11106)
  * doc: contrib/local.mk.example: include ENABLE_LTO  (#11097)
  * Fix two more flaky tests (#11095)
  * build: add support for building for FreeBSD under Sourcehut [skip ci]
  * vim-patch:8.0.0914: highlight attributes are always combined  (#10256)
  * paste: fix handling of "<" in cmdline (#11094)
  * test/functional/preload.lua: _set_fmode for Windows
  * Revert "win/os_env_exists(): workaround libuv bug #10734"
  * third-party: update libuv to v1.31.0
  * tests: busted: nvim handler: display durations always (#11075)
  * cmake/GetCompileFlags: include CMAKE_C_COMPILER_ARG1 (#11091)
  * timer_spec: fix/harden flaky tests (#11080)
  * tui_spec: improve "TUI paste: exactly 64 bytes" (#11086)
  * tui: flush ui buffer in tui_terminal_after_startup (#11083)
  * vim-patch:8.0.1754: ex_helpgrep() is too long #11084
  * vim-patch:8.0.1812: refactor qf_jump_to_usable_window() #11078
  * terminfo_start: flush buffer #11074
  * vim-patch:8.1.2059: fix for "x" deleting a fold has side effects
  * vim-patch:8.1.2052: using "x" before a closed fold may delete that fold
  * tests: make 'win_update redraws lines properly' more readable (#11068)
  * tests: unit: fix preprocess: pass -m32 for 32bit ABI (#11073)
  * screen: missing redraw/highlight for ruler in message area
  * env: use putenv_s for LC_ALL, LANG, etc. #11050
  * vim-patch:8.1.2060: "precedes" in 'listchars' not used properly
  * Fix "precedes" listchar behavior in wrap mode
  * checkhealth: skip python checks if intentionally disabled #11044
  * vim-patch:8.1.2055: profile: adjust line format #11058
  * vim-patch:8.1.0460: assert_fails() message argument #11051
  * vim-patch:8.0.1621: using invalid default value for highlight attribute
  * vim-patch:8.0.1529: assert_equalfile() does not close file descriptors
  * vim-patch:8.0.1776: in tests, when WaitFor() fails it doesn't say why
  * vim-patch:8.0.1771: in tests, when WaitFor() fails it doesn't say why
  * vim-patch:8.0.1733: incomplete testing for completion fix
  * vim-patch:8.0.1539: no test for the popup menu positioning
  * vim-patch:8.0.1109: timer causes error on exit from Ex mode
  * vim-patch:8.1.2058: function for ex command is named inconsistently
  * vim-patch:8.1.2054: compiler test for Perl may fail
  * vim-patch:8.1.1783: MS-Windows: compiler test may fail when using %%:S
  * screen: fix vcol counting with virtual text. Fixes #9941
  * vim-patch:8.1.2056: "make test" for indent files doesn't cause make to fail
  * Update runtime/indent/testdir to latest Vim runtime
  * vim-patch:8.1.1213: "make clean" in top dir does not cleanup indent test output
  * vim-patch:8.1.0599: without the +eval feature the indent tests don't work
  * vim-patch:8.1.0576: indent script tests pick up installed scripts
  * vim-patch:8.1.0545: when executing indent tests user preferences interfere
  * vim-patch:8.1.0496: no tests for indent files
  * win_update: fix redraw regression (#11027)
  * health#provider: fix duplicated output/stderr (#11048)
  * vim-patch:8.0.1770: assert functions don't return anything
  * vim-patch:8.0.1523: cannot write and read terminal screendumps
  * tests: improve error message with literat "~" directory (#11032)
  * tests: fix flaky 'scrollback' option deletes lines (only) if necessary (#11003)
  * server_requests_spec: fix assertion, pass Lua paths via args (#10875)
  * release.sh [ci skip]
  * nvim.appdata.xml [ci skip]
  * CI/AppVeyor: revert whitelist
  * fix api_level_6.mpack
  * nvim.appdata.xml [ci skip]
  * release.sh [ci skip]
  * version bump
  * NVIM v0.4.0
  * compositor: avoid transmitting invalid lines on double scroll
  * test/old: detect user modules for python,ruby
  * vim-patch:8.1.0220: Ruby converts v:true and v:false to a number
  * Context: rename "buflist" => "bufs"
  * API: nvim_get_context: "opts" param
  * release.sh: bump nvim.appdata.xml
  * autocmds: TermEnter, TermLeave #8550
  * test/old: skip python-bindeval tests
  * vim-patch:8.1.0212: preferred cursor column not set in interfaces
  * ci/travis: install pynvim outside of $HOME
  * test/old: skip failing ruby tests
  * vim-patch:8.0.1448: segfault with exception inside :rubyfile command
  * vim-patch:8.0.1134: superfluous call to syn_get_final_id()
  * vim-patch:8.1.2028: options test script does not work
  * vim-patch:8.1.0289: cursor moves to wrong column after quickfix jump
* Sat Sep 14 2019 mcepl@cepl.eu
- Update to version 0.4.0~git.1568471558.8c88d98df:
  * vim-patch:8.1.2023: no test for synIDattr() returning "strikethrough" (#11018)
  * lint
  * getdigits: introduce `strict`, `def` parameters
  * rename: getdigits_safe => try_getdigits
  * vim-patch:8.1.0719: too many #ifdefs [ci skip] #11016
  * vim-patch:8.1.2026: possibly using uninitialized memory #11013
  * test: fix failure on Windows (allow ".exe")
  * win/dist: nvim-qt v0.2.14 #11008
  * startup: fail if --embed with -es/-Es #10753
  * syntax, TUI: support "strikethrough"
  * vim-patch:8.1.0267: no good check if restoring quickfix list worked
  * vim-patch:8.1.0261: Coverity complains about a negative array index
  * vim-patch:8.1.0259: no test for fixed quickfix issue
  * vim-patch:8.1.0248: duplicated quickfix code
  * vim-patch:8.0.1772: quickfix: mixup of FALSE and FAIL, returning -1
  * UIEnter/UILeave: fire for embedder UI, builtin TUI
  * rename: UIAttach/UIDetach => UIEnter/UILeave
  * API/nvim_list_uis(): include "chan" field for TUI
  * UIAttach, UIDetach
  * UIAttach, UIDetach
  * lint
  * fixup! cursor_shape: check if modep is nonnull
  * Remove excess <stdint.h>
  * tests: fix system_spec when run with clipboard manager (#10956)
  * build: dependencies: specify minimum libvterm (#10997)
  * rename: SplitEvent => MulticastEvent #10989
* Wed Sep 11 2019 mcepl@cepl.eu
- Update to version 0.4.0~git.1568231806.7652904f7:
  * eval: wait(): always spin up dummy-timer #10990
  * paste: fix paste in terminal mode
  * doc
  * doc: nvim_ui_pum_set_height  [ci skip]
  * spell: assert nonull pointers
  * cursor_shape: check if modep is nonnull
  * regexp: assert nonnull pointer for regnext()
  * quickfix: fix pvs/v547 warning
  * terminal: fix rgb rendering of palette colors
  * lint / test grouping
  * Changes for new VTermColor struct
  * bump libvterm to 0.1 + memleak patch
* Tue Sep 10 2019 mcepl@cepl.eu
- Update to version 0.4.0~git.1568089424.477113d1a:
  * vim-patch:8.0.1309: cannot use 'balloonexpr' in a terminal #10983
  * vim-patch:8.0.0941: existing color schemes don't like StatusLineTerm
  * vim-patch:8.0.0937: user highlight groups not adjusted for terminal
  * provider: has("python3_dynamic") et al. #10980
  * doc/API/lua: detaching Lua buffer callbacks
  * doc: StatusLineTerm, StatusLineTermNC
  * doc: |api-fast| [ci skip]
  * version.c: update [ci skip] #10961
  * doc: eliminate msgpack_rpc.txt [ci skip]
  * doc
  * paste: fix normal-mode paste by different approach #10976
* Mon Sep  9 2019 mcepl@cepl.eu
- Update to version 0.4.0~git.1568001516.9e0ce1a15:
  * vim-patch:8.1.1197: when starting with multiple tabs file messages is confusing
  * paste: insert before cursor always
  * paste: do not clobber msg area for small pastes
  * paste/cmdline: discard all chunks after first line
  * vim-patch:8.0.0970: passing invalid highlight id #10972
  * paste: reset 'paste' option immediately #10974
  * vim-patch:8.1.2007: no test for what 8.1.1926 fixes #10970
  * ex_getln.c: fix <S-Tab> not triggering pum when wildoptions=pum (#10042)
  * update tests for new resize behavior (resize at pager, but not at :!cmd)
  * rpc: allow handling of nvim_ui_try_resize at the pager
  * messages: redraw after resize in pager
  * messages: batch draw :map
  * refactor: allow us to process a child queue only while waiting on input
  * tests: fix flaky "TUI FocusGained/FocusLost in terminal-mode" #10754
  * Add nvim_ui_pum_set_height to api
  * shada: initialize jumplist before search pattern (#10964)
  * vim-patch:8.1.1716: old style comments are wasting space
  * vim-patch:8.0.1550: various small problems in source files
  * vim-patch:8.1.1988: :startinsert! does not work the same way as "A"
  * vim-patch:06fe74aef726
  * vim-patch:56c860c315c5
  * vim-patch:088e8e344352
* Sat Sep  7 2019 Matej Cepl <mcepl@suse.com>
- Add native-lsp.patch as a current snapshot of gh#neovim/neovim#10222
* Sat Sep  7 2019 mcepl@cepl.eu
- Update to version 0.4.0~git.1567819017.158b78062:
  * test: Eliminate expect_err
  * test: Rename meth_pcall to pcall_err
  * termdebug.vim: use style=minimal in popups #10904
  * version.c: update [ci skip] #10942
  * build: rename CMake find modules for LibFindMacros #10928
  * runtime: :TOhtml workaround for missing 'vts' option #10960
  * build: cmake: GetCompileFlags: include CMAKE_C_FLAGS (#10957)
  * test: properly test missing clears after scroll
  * test: add tests for pager glitches and crashes
  * messages: fix crashes with scrollback
  * messages: fix missing MsgArea highlighting on/after "-- more --" message
  * messages: fix cut lines in scrollback upon overflow
  * tests: do_rmdir(): improve error handling #10955
  * vim-patch:8.0.1332: enhance quickfix highlighting #10259
  * stdpaths_get_xdg_var: consider empty env vars #10953
  * build: fail with CLANG_TSAN + USE_GCOV #10958
  * screen: redrawdebug=nothrottle
  * vim-patch:8.1.0561: MSCV error format has changed #10952
  * test/shada_spec: avoid exit_event race #10951
  * fixup! test/wildmode_spec: fix flaky test
  * test/wildmode_spec: fix flaky test
  * anchor float to buffer position
  * vim-patch:8.1.1501: new behavior of b:changedtick not tested
  * vim-patch:8.1.1498: ":write" increments b:changedtick even though nothing changed
  * tests: scrollback_spec: use shell-test instead of awk (#10914)
  * version.c: update [ci skip] #10308
  * Log signals handled in deadly_signal (#10939)
  * test/mode_spec: increase 'matchtime' to fix flaky
  * test: is_os() #10933
  * netrw.vim: workaround gx bug #10938
  * only check got_int with ex_echo
  * move test
  * Check got_int in msg_multiline_attr
  * vim-patch:8.1.0145: test with grep is failing on MS-Windows
  * vim-patch:8.0.1844: superfluous quickfix code, missing examples
  * vim-patch:8.1.1946: memory error when profiling a function without a script ID
  * vim-patch:8.0.1752: qf_set_properties() is to long
  * vim-patch:8.1.0515: reloading a script gives errors for existing functions
  * vim-patch:8.1.0365: function profile doesn't specify where it was defined
  * vim-patch:8.1.0309: profiling does not show a count for condition lines
  * [squash] Fix errors when porting
  * Change test because maparg was changed to also return lnum
  * vim-patch:8.1.0362: cannot get the script line number when executing a function
  * test: enable "exit event follows stdout, stderr" [ci skip] #10929
  * shada/context: fully remove jumplist duplicates #10898
  * f_jobwait: cleanup
  * jobwait(): fix race if job exits before waiting on it
  * test/wildmode_spec: fix flaky test
  * test/job_spec: improve visibility of flaky test
  * tests: assert:set_parameter('TableFormatLevel', 100) #10925
  * vim-patch.sh: fix "unbound variable" error with Bash < 4.4  [ci skip] (#10917)
  * vim-patch:8.1.1063: insufficient testing for wildmenu completion
  * vim-patch:8.1.0046: loading a session file fails if 'winheight' is big
  * vim-patch:8.0.1806: InsertCharPre causes problems for autocomplete
  * vim-patch:8.0.1768: SET_NO_HLSEARCH() used in a wrong way
  * api: make try_end clean-up after an exception properly. Fixes #10809
  * vim-patch:8.0.1729: no comma after last enum item
  * vim-patch:8.0.1697: various tests are still a bit flaky
  * screen: initialize screen properly with early `set display-=msgsep`
  * vim-patch:8.0.0858: check if job terminal is running #10908
  * test/uname(): always lowercase
  * test/OpenBSD: skip some tests
  * test: shell-test.c: flush all streams
  * screen.lua: dump payload on handler failure
  * test: "can have two timers": retry()
  * CI/OpenBSD: run functional tests
  * API: nvim_buf_set_lines: handle 'nomodifiable' #10910
  * vim-patch:8.0.1653: screen dump is made too soon (#10911)
  * PVS/V547: Expression is always false
  * API: make nvim_win_set_option() set window-global, not buffer-local #9110
  * paste: redraw at end
  * paste: one undo-block per stream
  * vim-patch:8.0.1534: C syntax test fails in gvim #10909
  * fixup! eval: add wait() test
  * eval: add wait() test
  * eval: add wait()
  * screen: add some documentation of internals of msg_grid implementation
  * test: assert_alive()
  * test: use shell-test (avoid system shell)
  * test/inccommand_spec: avoid indeterminism
  * vim-patch:8.1.0141: :cexpr no longer jumps to the first error #10901
  * vim-patch:8.0.1217: remote eval to inspect vars in :debug #10903
  * vim-patch:8.0.1260: using global variables for WaitFor()
  * vim-patch:8.0.1246: popup test has an arbitrary delay
  * vim-patch:8.0.1241: popup test is flaky
  * test/ui: update tests for new msg_grid implementation
  * screen: use dedicated message grid
  * batch draw :ls
  * test/ui: make screen:expect() print full state when height does not match
  * vim-patch:8.1.1950: using NULL pointer after an out-of-memory (#10902)
  * tui/input: remove "cancel paste" logic which should be redundant
  * api: make nvim_put support "\022{NUM}" regtype as returned by getregtype()
  * events: loop_schedule() is unclear, rename it loop_schedule_fast()
  * tui/input: defer nvim_paste properly.
  * vim-patch:8.1.1947: when executing one test the report doesn't show it #10893
  * vim-patch:8.1.1941: getftype() test fails on Mac #10894
  * vim-patch:cb00f0393 (#10892)
  * vim-patch:8.0.0930: terminal buffers are stored in the viminfo file (#10889)
  * scripts/vim-patch.sh: massage args for git-log  [ci skip] (#10888)
  * vim-patch:8.1.0950: using :python sets 'pyxversion' even when not executed (#10891)
  * vim-patch:8.1.0212: preferred cursor column not set in interfaces (#10890)
  * test: vim.paste() cancel
  * API: nvim_paste: add `crlf` parameter
  * tests: check_logs: improve error message (#10887)
  * shell-test: remove REP_NODELAY, less delay with REP
  * Revisit out_data_decide_throttle
  * tests: fix Test_tagfiles: use Vim's 'tags' (#10883)
  * vim-patch:8.1.1937: errors when using javascriptreact #10885
  * vim-patch:8.1.0233: "safe" argument of call_vim_function() is always FALSE
  * vim-patch:8.1.1938: may crash when out of memory
  * paste: break lines at CR, CRLF #10877
  * Fix test/busted/outputHandlers/TAP.lua (#10881)
  * vim-patch:8.1.0193: terminal debugger buttons don't always work (#10874)
  * third-party: remove msvc-compat/unistd.h  (#10465)
  * tests: use runtime from build for doc/tags with :help (#10479)
  * vim-patch:8.0.0303: shift_delete_registers() #10868
  * doc: man.vim #10817
  * API: TRY_WRAP() for "abort-causing non-exception errors"
  * vim-patch:8.1.1932: ml_get errors after append() #10866
  * paste: handle 'nomodifiable'
  * clang/"null pointer dereference" #10864
  * paste: make vim.paste() "public"
  * paste: handle vim.paste() failure
  * paste: tickle cursor
  * paste: implement redo (AKA dot-repeat)
  * paste: insert text "before" cursor in Insert-mode
  * API: nvim_paste
  * paste: workaround typeahead race
  * paste: phases, dots
  * API: nvim_put: "follow" parameter
  * API: nvim_put: always PUT_CURSEND
  * test/tui_spec: connect to child session
  * API: nvim_put: Avoid "N more lines" message
  * paste: edge-case: handle EOL at end-of-buffer
  * paste: test
  * paste: use nvim_put()
  * API: nvim_put #6819
  * API: nvim_put #6819: try to fix Insert, Visual
  * API: nvim_put #6819
  * paste: use chansend() in Terminal-mode
  * paste: fixup tests
  * paste: abort paste if handler does not return true
  * TUI/paste: always flush on paste mode-change
  * TUI/paste: define paste function as Lua builtin
  * lua/stdlib: cleanup
  * log: log_key()
  * TUI/paste: push bytes directly (avoid libtermkey)
  * TUI/paste: collect data, invoke user callback #4448
  * paste: WIP #4448
  * build: third-party: enable CXX language earlier (#10862)
  * vim-patch:8.1.1931: syntax test fails
  * vim-patch:8.1.1930: cannot recognize .jsx and .tsx files
  * clang/"dereference of null pointer" #10856
  * timer_spec: shorter timeout with "doesn't mess up the cmdline" (#10769)
  * vim-patch:8.1.1923: some source files are not in a normal encoding (#10852)
  * runnvim.sh: lint (shellcheck) (#10851)
  * third-party: use neovim/unibilium (#10677)
  * vim-patch:8.1.1790: :mkvimrc is not tested
  * findoption_len: treat viminfo/viminfofile as aliases
  * vim-patch:8.1.1926: redraw cursorline after putting line above #10849
  * vim-patch:8.1.1913: not easy to compute the space on the command line (#10845)
  * teardown: fix win_free_all() heap-use-after-free #10839
  * vim-patch:8.1.1924: using empty string for current buffer is unexpected
  * vim-patch:8.1.1111: it is not easy to check for infinity
  * vim-patch:7.4.1407
  * vim-patch:8.1.1757: text added with appendbufline() isn't displayed
  * vim-patch:8.0.1236: Mac features are confusing #10837
  * vim-patch:8.1.0187: getwininfo() and win_screenpos() return different numbers
  * vim-patch:8.0.1386: cannot select modified buffers with getbufinfo()
  * vim-patch:8.1.0039: cannot easily delete lines in another buffer
  * vim-patch:8.1.0037: cannot easily append lines to another buffer
  * API: fix nvim_command_output buffer overflow (#10830)
  * vim-patch:8.1.1897: may free memory twice when out of memory (#10827)
  * tui: handle Smulx extension capability (extended underline) (#9097)
  * -u NONE for no syntax highlighting
  * vim-patch:8.1.1893: script to summarize test results can be improved
  * vim-patch:8.1.1478: still an error when running tests with the tiny version
  * vim-patch:8.1.1477: test summary fails in the tiny version
  * vim-patch:8.1.1488: summary of tests has incorrect failed count
  * vim-patch:8.1.1476: no statistics displayed after running tests
  * vim-patch:8.1.1483: skipped tests are not properly listed
  * vim-patch:8.1.0811: too many #ifdefs
  * test: fix problem of breaking user's viminfo (#10824)
  * ci: AppVeyor: exitIfFailed with old tests  (#10187)
  * vim-patch:8.1.0888: the a: dict is not immutable as documented (#10819)
  * edit: add nonnull func attribute
  * edit: compl_started,compl_used_match are bool
  * vim-patch:8.1.1124: insert completion flags are mixed up
  * fixup! test/functional/helpers.lua: env: forward also TSAN_OPTIONS/MSAN_OPTIONS
  * test/functional/helpers.lua: env: forward also TSAN_OPTIONS/MSAN_OPTIONS
  * src/nvim/testdir/runnvim.vim: improve escaping of non-printables
  * tests: support msg with global_helpers.ok (#10820)
  * oldtest: windows: revert setting shellslash individually (#10189)
  * win: stream: reset tty stream on close
  * tests: screen: notification_cb: improve assertion message
  * .gitignore: src/nvim/testdir/*.tlog
  * test/functional/ui/mode_spec: improve "ui mode_change event" (#10816)
  * tests: screen: notification_cb: improve assertion message
  * tests: timer_spec: lower timeout, avoids flakiness
  * vim-patch:8.1.1890: ml_get error when deleting fold marker
  * vim-patch:8.1.1887: the +cmdline_compl feature is not in the tiny version
  * src/nvim/README: revisit sanitizer section  [ci skip] (#10780)
  * tests: win: enable buffer focus test
  * test: win: enable WinEnter terminal test
  * test: win: enable output_spec test
  * Unreserve :X #10807
  * CI/AppVeyor: revert "skip MSVC_32 for non-PR" [skip travis] #10805
  * ui: transmit "blend=" property of highlight attributes
  * CI/OpenBSD: run oldtest #10797
  * Change to use v:progpath instead of constant [skip ci]
  * vim-patch:8.1.1839: insufficient info when test fails because of screen size
  * vim-patch:8.1.1679: test using SwapExists autocommand file may fail
  * vim-patch:8.1.1870: using :pedit from a help file sets help filetype
  * test/ui: properly test win_hide by explicitly marking hidden grids
  * ui: use Window type in win_pos consistently with win_float_pos
  * Fix test failure on Windows [skip travis]
  * Change value of cpo [skip travis]
  * Remove test52
  * Change test execution conditions
  * Add target fixff to testdir/Makefile
  * Fix get_path_cutoff() on Windows
  * Remove code that is no longer needed by set shellslash
  * Change to set shellslash to test under same conditions as vim
  * vim-patch:8.1.1860: map timeout test is flaky
  * vim-patch:8.1.1858: test for multi-byte mapping fails on some systems
  * vim-patch:8.1.1857: cannot use modifier with multi-byte character
  * vim-patch:8.1.1854: now another timer test is flaky #10791
  * CI/OpenBSD: Initial sourcehut dispatch file #10792
  * CI/AppVeyor: skip MSVC_32 for non-PR builds [skip travis] #10786
  * keymap: allow modifiers to multibyte chars, like <m-ä>
  * vim-patch:8.1.1852: timers test is flaky #10788
  * Change to output status on failure
  * windows: ok(#children >= 3 and #chidlen <= 5)
  * windows: ok(#children >= 4 and #children <= 5)
  * Remove TSan suppression config  [skip appveyor]
  * emsg_multiline: log Vim errors (#10778)
  * TUI: do not use "starting" global mutated by main thread
  * src/nvim/CMakeLists.txt: use compile options/definitions
  * get_compile_flags: also look at target properties
  * CI/travis: git clone -q #10781
  * build/win: fix warnings
  * os/: remove redundant define
  * utf16_to_utf8: align with libuv
  * utf8_to_utf16: align with libuv
  * tests: skip "API nvim_parse_expression" on MSVC_32 (#10773)
  * build: TSan: add src/.tsan-suppressions
  * ci: Travis: build.sh: use cat "-vet" for osx
  * pyxversion: fix logic error #10759
  * ci: Travis: homebrew: update=false  [skip appveyor]
  * clang/"null pointer dereference" #10776
  * ci: Travis: check logs for TSan also  (#10775)
  * api: nvim_win_open() style="minimal" should disable 'foldcolumn'
  * compositor: handle invalid screen positions after resize gracefully
  * clipboard: handle/avoid SIGTERM with previous owner #10765
  * tests: fix/improve "jobwait returns -1 when timed out" #10767
  * tests: include `timer_start` in duration #10772
  * mksession: use exists(':tcd'), not has('nvim') #10770
  * vim-patch:8.1.0456: running test hangs when the input file is being edited (#10764)
  * tests: use larger timeout with "timers can be stopped from the handler" (#10760)
  * style
  * startup: handle 'guicursor' after user config
  * vim-patch:8.1.1842: test listed as flaky should no longer be flaky
  * vim-patch:8.0.1179: Test_popup_and_window_resize() does not always pass
  * clang/"null pointer dereference" #10755
  * vim-patch:8.1.1843: might be freeing memory that was not allocated (#10756)
  * build: link libraries by full path (for luv.so) (#10661)
  * testdir/test_popup.vim: sync/align with Vim (#10751)
  * ex_getln.c: fix compute_cmdrow() not resetting lines_left (#10749)
  * free_buffer: rework b:changedtick handling #9163
  * vim-patch:8.0.1193: crash when wiping buffer after getbufinfo()
  * ci: AppVeyor: branches: only: master  (#10746)
  * win/env: Vim-compat: Empty string deletes env var #10743
  * vim-patch:8.1.1462: MS-Windows: using special character requires quoting
  * vim-patch:8.1.1461: tests do not run or are not reliable on some systems
  * test_source.vim: move Test_source_sandbox
  * win: expand nested env var #10662
  * clang/"Argument with 'nonnull' attribute passed null" #10739
  * api/window: disallow closing non-current window in cmdwin state
  * testdir/test_taglist.vim: move Test_tagsfile_without_trailing_newline
  * vim-patch:8.1.0911: tag line with Ex command cannot have extra fields
  * API: nvim_win_close: Fix closing cmdline-window #10087
  * win/os_env_exists(): workaround libuv bug #10734
  * test/cmdline_spec: adjust "no-op"
  * test/environ_spec: Windows treats empty as undefined
  * vim-patch:8.1.1458: crash when using gtags #10704
  * exists(): return false for empty env var #10657
  * channels: reflect exit due to signals in exit status code (#10573)
  * tests/functional: expect_msg_seq: use load_adjust (#10727)
  * clang/"Null passed as a nonnull parameter" #10718
  * :terminal : update buffer when switching tabpage #10700
  * vim-patch:8.1.1540: cannot build without +eval #10729
  * test: Minimize shada/helpers.lua #10728
  * f_spellbadword: set len=0 for non-found word
  * vim-patch:8.1.0200: spellbadword() not tested
  * vim-patch:8.1.0199: spellbadword() does not check for caps error
  * lua: minimal UTF-16 support needed for LSP
  * vim-patch:8.1.1824: crash when correctly spelled word is very long (#10725)
  * tests: use module pattern with test/functional/helpers.lua (#10724)
  * build: Makefile: use _opt_pylint  [ci skip] (#10720)
  * tests: output_spec: use shell-test REP_NODELAY (#10726)
  * build/MSVC: Fix HAVE_ICONV_H #10697
  * build: port FindLibVterm to LibFindMacros (#10395)
  * build: clean up / remove X_USE_STATIC (#10713)
  * ci: AppVeyor: fix upload of coverage for oldtest (#10721)
  * lint
  * remove !has_mbyte branches
  * includes
  * move ins_char
  * lint
  * move del_lines
  * lint/sync: truncate_line
  * move truncate_line
  * lint/sync: open_line
  * move open_line
  * move copy_indent (from nvim's indent.c)
  * move del_bytes
  * move del_char, del_chars
  * move ins_str
  * move ins_char_bytes
  * move ins_bytes, ins_bytes_len
  * move unchanged
  * move changed_lines
  * move deleted_lines, deleted_lines_mark, changed_lines_buf
  * move appended_lines_mark
  * move appended_lines
  * remove inserted_bytes (comes via text properties, v8.1.0678)
  * move changedOneline, changed_bytes
  * move changed_common
  * move changed_int/changed_internal
  * move changed
  * move change_warning
  * header
  * orig src/nvim/change.c
  * Fix lualint: remove unused var
  * cmakelists: fixed tests to avoid clang warnings (#10705)
  * tests: more cleanup of plugin/shada_spec
  * build: lint: fix exit with optional pylint
  * lua: support getting UTF-32 and UTF-16 sizes of replaced text
  * Fix list_features to include space after first feature (#10711)
  * build: move pylint to Makefile, optional with "make lint" (#10714)
  * tests: unit.helpers: provide string with write errors (#10715)
  * lua: add {old_byte_size} to on_lines buffer change event
  * remove DYNAMIC_ICONV
  * vim-patch:8.1.1467: cscope test fails
  * vim-patch:8.1.1465: allocating wrong amount of memory
  * f_environ: cleanup/refactor
  * vim-patch:8.1.1305: there is no easy way to manipulate environment variables
  * clang/"dead assignment": screen.c #10702
  * clang/"dead assignment": suppessed
  * test/mbyte_spec: skip broken test on QuickBuild
  * test: Eliminate plugin/helpers.lua
  * vim-patch:8.1.1439: ga_grow(): 1.5x growth rate #10699
  * lua: add vim.in_fast_event() to check if we are in a luv callback
  * lua: do not crash on syntax error in debug.debug()
  * lua: immediate-callback safe print()
  * test/man_spec: remove plugin_helpers.reset()
  * test/mbyte_spec: skip broken test on QuickBuild
  * test: isCI(): add "name" parameter
  * tests: fix flaky "TermClose … fast-exiting terminal job stops"
  * vim-patch:8.1.1383: warning for size_t/int mixup (#10694)
  * :doautocmd : Never show "No matching autocommands" #10689
  * vim-patch:8.1.1311: test: abort autocmd with exception #10692
  * vim-patch:8.1.1251: test completion of mapping keys #10691
  * Makefile: only use pattern rules with BUILD_TYPE=Ninja  (#10687)
  * runtime/matchit.vim: workaround broken 'packpath'
  * provider: check #Call() if g:loaded_xx_provider=2
  * health.vim: check has("debug")
  * provider: skip non-provider has() feature-names
  * provider: g:loaded_xx_provider=2 means "enabled and working"
  * provider: decide status by g:loaded_xx_provider
  * provider: let providers decide their status
  * doc: update 'shellredir' advice for powershell #10686
  * vim-patch:8.1.1237: error for using "compl", reserved word in C++
  * vim-patch:8.1.1796: :argdo is not tested
  * build: require unibilium>=2.0 (#10681)
  * ci: Travis: move gcc-functionaltest-lua to 2nd stage (#10682)
  * vim-patch:8.1.1775: error message may be empty in filetype test
  * vim-patch:8.1.1762: some filetype rules are in the wrong place
  * vim-patch:8.1.1761: filetype "vuejs" causes problems for some users
  * vim-patch:8.1.1187: cannot recognize Pipfile
  * terminfo_start: use unibi_from_term, skip without TERM (#10670)
  * runtime/optwin.vim: missing 'previewpopup' feature
  * doc: remove "{not available ...}" noise
  * vim-patch:5477506a9f01
  * vim-patch:85850f3a5ef9
  * vim-patch:396e829fa355
  * vim-patch:6c1e1570b134
  * vim-patch:12ee7ff00b91
  * vim-patch:773a97c254d0
  * vim-patch:61da1bfa6c6b
  * vim-patch:7dd64a3e57d2
  * vim-patch:68e6560b84f1
  * cleanup
  * ci: Travis: move coverage job to first stage (#10673)
  * vim-patch:a6c27c47ddf0
  * vim-patch:911ead126903
  * vim-patch:62e1bb4a111e
  * vim-patch:723dd946f948
  * vim-patch:63b74a8362b1
  * vim-patch:26967617a30e
  * vim-patch:f6b401090e81
  * vim-patch:4c92e75dd4dd
  * runtime: move matchit.vim to /pack/dist/opt/
  * stream: log unwritten bytes, if any #10663
  * process_stop: uv: do not close stdin first/explicitly #10584
  * fileio: port hotfix from patch 8.1.1379
  * vim-patch:8.1.1374: check for file changed triggers too often
  * lint
  * vim-patch:8.1.1780: warning for file no longer available is repeated
  * ci: Travis: improve/revisit caching (#10358)
  * lint: helptags_one
  * vim-patch:8.1.0572: stopping a job does not work properly on OpenBSD
  * tests: runnvim.vim: do not call jobstop() (#10659)
  * Makefile: use pattern rules for build/.deps  [ci skip] (#10366)
  * gen_eval.lua: use correct name in usage
  * tests: use Vim's version for patch 8.1.0005
  * vim-patch: handle tags, pass through git-log options  (#10140)
  * clang/"null pointer dereference": ex_cmds.c
  * ci: pylint target via flake8
  * py: flake8 fixes
  * scripts: autopep8
  * vim-patch:94688b8a2a1f
  * vim-patch:314dd79cac2a
  * vim-patch:2a953fcf107d
  * vim-patch:d09091d4955c
  * vim-patch:4c05fa08c973
  * vim-patch:c8c884926750
  * vim-patch:c33181c44ccb
  * vim-patch:9d87a37ee9d8
  * vim-patch:d47d52232bf2
  * vim-patch:b730f0c7ba36
  * vim-patch:f0d58efc9dc4
  * vim-patch:ba3ff539303c
  * vim-patch:790c18bfa5df
  * PVS/V507: suppress false positive #10647
  * vim-patch:8.1.0053 use typval_T in the caller of call_vim_function Problem:	unreliable types for complete function arguments Solution:	fix argument type for functions w/ unreliable type conversion(Ozaki Kiichi) vim/vim#2993
  * build/macOS: enable fallthrough attribute #10653
  * vim-patch:8.1.1086: too many curly braces
  * buffer: add attributes to pure functions
  * vim-patch:8.1.1049: when user tries to exit with CTRL-C message is confusing
  * vim-patch:8.1.1041: test for Arabic no longer needed
  * vim-patch:8.1.1394: not restoring t_F2 in registers test
  * vim-patch:8.1.1005: test fails because t_F2 is not set
  * lint: makemap
  * pvs/V560: part of conditional expression is always false
  * vim-patch:8.1.1138: add CompleteChanged #10644
  * vim-patch:8.1.0017: shell command completion has duplicates #10616
  * clang/"dead assignments" #10620
  * TextYankPost: spurious/too-early dispatch during delete #10392
  * PVS/V547: expression is always true/false #10640
  * vim-patch:8.1.0990: floating point exception with "%%= 0" and "/= 0"
  * PVS/V512: memcpy overflow/underflow #10642
  * vim-patch:8.1.1765: get(func, dict, def) does not work properly
  * PVS/V560: condition is always false #10638
  * vim-patch:8.0.1753: fix various warnings #10639
  * context: shada_encode_regs(): init WriteMergerState #10637
  * PVS/V560: expression is always false/true #10623
  * vim-patch:7.4.2213: runtime parts with EndOfBuffer port #10635
  * ci: Travis: no need for asan_symbolize (#10627)
  * src/clint.py: flake8 fixes  [ci skip] (#10631)
  * vim-patch:b1c9198af (#10634)
  * build/tests: remove pre/uv.h #10531
  * PVS/V560: condition is always true #10630
  * PVS/V560: condition is always true #10624
  * pvs/V560: part of conditional expression is always true (#10629)
  * Fix clint error
  * vim-patch:8.1.1759: no mode char for terminal mapping from maparg()
  * vim-patch:8.1.0053 use typval_T in the caller of call_vim_function Problem:	unreliable types for complete function arguments Solution:	fix argument type for functions w/ unreliable type conversion(Ozaki Kiichi) vim/vim#2993
  * vim-patch:8.1.1748: :args output is not aligned (#10625)
  * API: Context: save/restore
  * vim-patch:8.1.0956: context:0 in 'diffopt' #10622
  * eval: context: add ctx-family functions
  * API: Context
  * API: Context
  * vim-patch:8.1.53 use typval_T in the caller of call_vim_function Problem:	unreliable types for complete function arguments Solution:	fix argument type for functions w/ unreliable type conversion(Ozaki Kiichi) vim/vim#2993
  * ci: AppVeyor: DEPS_BUILD_DIR is not a CMake variable  [ci skip] (#10613)
  * ci: Travis: single osx job  [ci skip] (#10614)
  * ci: Travis: gcc-9: use gcov-9  (#10609)
  * tests: test_arglist.vim: align with Vim  [ci skip] (#10612)
  * ci: Travis: remove clang-tsan from allowed failures [skip ci] (#10591)
  * tests: win: fix "cat" with PowerShell
  * tests: use "cat" also on Windows
  * vim-patch:8.1.1747: unused variables #10605
  * Revert "vim-patch:8.1.0430: Xargadd file left behind after running test"
  * vim-patch:8.1.0404: accessing invalid memory with long argument name
  * cleanup: remove mch_fopen in favor of os_fopen
  * os/fs: introduce os_fopen()
  * PVS/V768: do use enum as bool #10582
  * regexp: add function attributes
  * vim-patch:8.1.0913: CI crashes when running out of memory
  * vim-patch:8.1.0910: crash with tricky search pattern
  * vim-patch:8.1.0907: CI tests on AppVeyor are failing
  * vim-patch:8.1.0905: complicated regexp causes a crash
  * regexp: use fixed types to avoid overflow
  * Checks for overflow when parsing string to int
  * vim-patch:8.1.0908: can't handle large value for %%{nr}v in regexp
  * vim-patch:8.1.1746: ":dl" is seen as ":dlist" instead of ":delete"
  * vim-patch:8.1.0903: struct uses more bytes than needed
  * vim-patch:8.1.0899: no need to check restricted mode for setwinvar()
  * coverage: use "cd" with gcovr (#10594)
  * vim-patch:8.1.1740: exepath() doesn't work for "bin/cat" (#10556)
  * vim-patch:8.1.1738: testing lambda with timer is slow (#10590)
  * third-party: download: retry (#10599)
  * ci: RunTests: ensure that the logfile gets displayed (#10597)
  * sign: REMOVE FEAT_SIGN_ICONS, dead code #10595
  * tests: AppVeyor: fix test/functional/ex_cmds/arg_spec.lua (#10598)
  * vim-patch:8.1.1737: :args command that outputs one line gives more prompt
  * vim-patch:8.0.1738: ":args" output is hard to read
  * tests: fix/improve Screen:expect_unchanged (#10577)
  * ci: restore accidentally removed config (#10592)
  * tests: re-enable "tab drag in tabline to the left moves tab left" (#10588)
  * env: invalid pointer after os_setenv() #10558
  * win/TUI: workaround libuv LF => CRLF conversion #10558
  * Revert "vim-patch:8.0.1723: using one item array size declaration is misleading" (#10583)
  * build: GetBinaryDeps: move include, fix doc (#10579)
  * shell-test: fix REP for count larger than uint8_t (#10581)
  * PVS/V1019: "readability" warning #10566
  * tests: make TERM=interix test pending (#10576)
  * build: fix gcc warnings #10568
  * vim-patch:8.1.0706: introduce :redrawtabline #10570
  * build: remove -Wno-array-bounds workaround #10484
  * test/helpers: improve pattern with module functions (#10421)
  * vim-patch:8.1.1724: too much overhead checking for CTRL-C #10564
  * os_can_exe: remove char_u
  * win: jobstart(), system(): $PATHEXT-resolve exe
  * move: assert nonnull wp pointer
  * vim-patch:8.1.0856: when scrolling a window the cursorline is not always updated
  * vim-patch:8.1.1720: crash with very long %%[] pattern
  * vim-patch:8.1.0789: session sets v:errmsg #10553
  * test: shell-test.c: "REP" command: flush, wait 1ms #10552
  * screen.lua: always print keyword-args snapshot
  * screen.lua: expect_unchanged(), get_snapshot()
  * vim-patch:8.1.0754: preferred column when setting 'cursorcolumn' #10549
  * test: shell-test.c: flush stdout for REP #10548
  * [RFC]vim-patch:8.1.{749,1715} #10545
  * reltimefloat(): allow negative result #10544
  * doc [ci skip] #10383
  * PVS/V1026: possible overflow in a loop #10529
  * lint
  * pvs/V560: A part of conditional expression is always true
  * pvs/V560: A part of conditional expression is always true
  * refactor: use int for Columns and Rows
  * refactor: enable -Wconversion for ex_getln.c
  * option_defs.h: fix incorrect definition #10542
  * test: Force $TEST_FILE to relative path [ci skip] #10535
  * vim-patch:8.1.0740: Tcl test fails (#10540)
  * Revert "Downgrade to clang-4.0 to avoid false-positive warnings from clang"  [skip appveyor] (#10487)
  * pvs/V1037: two case branches doing the same thing (#10527)
  * PVS/V1037: suppress warning #10526
  * vim-patch:8.1.0732: cannot build without the eval feature
  * vim-patch:8.1.0729: there is a SourcePre autocommand event but not a SourcePost
  * ci: Travis: use gcc9 with gcov job [skip appveyor] (#10480)
  * PVS/V1037: suppress warning #10528
  * PVS/V1037: redundant switch-case branches #10519
  * tests: fix "system() … prints verbose information" (#10532)
  * ci: Travis: ccache: use CCACHE_HASHDIR  [skip appveyor]
  * build: fix handling of install prefix with CMAKE_EXTRA_FLAGS (#10530)
  * jobstop(): close channel before process_stop() #10522
  * vim-patch:8.1.0715: superfluous redraw_win_later() #10523
  * tests: move "busted" dir to "test" (#10518)
  * tests: shell-test: use count for REP (#10514)
  * viml/profile: revert proftime_T to unsigned type #10521
  * PVS/V1028: cast operands, not the result #10505
  * PVS/V108: cast operands, not the result #10501
  * PVS/V1028: cast operands, not the result #10503
  * lint
  * pvs/V1028: cast operands, not the result
  * PVS/V1028: cast operands, not the result #10502
  * third-party: busted 2.0.0-0 (#10517)
  * vim-patch:8.1.0686: when 'y' is in 'cpoptions' yanking for the clipboard changes redo
  * vim-patch:8.1.0641: no check for out-of-memory when converting regexp
  * vim-patch:8.1.0630: "wincmd p" does not work after using an autocmd window
  * vim-patch:8.1.0623: iterating through window frames is repeated
  * vim-patch:8.1.0583: using illogical name for get_dict_number()/get_dict_string()
  * vim-patch:8.1.1651: suspend test is flaky on some systems
  * vim-patch:8.1.0533: screendump tests can be flaky
  * vim-patch:8.1.0531: flaky tests often fail with a common error message
  * vim-patch:8.1.1012: memory leak with E461
  * vim-patch:8.1.0833: memory leak when jumps output is filtered
  * vim-patch:8.1.1221: filtering does not work when listing marks
  * vim-patch:8.1.0505: filter command test may fail if helplang is not set
  * vim-patch:8.1.0495: :filter only supports some commands
  * lint
  * pvs/V1037: two case-branches perform the same action
  * viml/profile: cast os_hrtime() result
  * PVS/V781: suppress false positive #10516
  * PVS/V1028: cast operands, not the result #10496
  * lint
  * pvs/V1028: cast operands, not the result
  * Fix missing CursorHoldI events (#3758)
  * PVS/V1028: cast operands, not the result #10507
  * PVS/V1028: cast operands, not the result #10498
  * third-party: use CXX only for BuildGperf (#10512)
  * Fix is_executable_in_path() on Windows (#10468)
  * build: propagate sysroot to C++ deps (gperf) #10491
  * PVS/V590: redundant condition #10510
  * PVS/V547: expression is always false #10511
  * PVS/V1028: cast operands, not the result #10508
  * PVS/V1028: cast operands, not the result #10508
  * checkhealth: try yarn if npm is missing #10490
  * PVS/V1028 ugrid.c:76 (#10495)
  * highlight: expose builtin highlight groups using hl_group_set event
  * syntax: refactor syn_list_header to not use magic value
  * syntax: fix missing newlines in execute("syn list"). fixes #10467
  * gitignore: ignore idea/clion
  * floats: fix 'winblend' on top of doublewidth chars.
  * viml/profile: revert gettimeofday() #10488
  * PVS/V547: dead code #10459
  * tests: use vim.inspect (#10485)
  * vim-patch:8.1.1660: assert_fails() inside try/catch #10472
  * build: fix check_c_compiler_flag for -Wno-… (#10483)
  * oldtest: more compact output with "clean" target (#10477)
  * pvscheck.sh: Remove --verbose flag #10473
  * vim-patch:8.1.1173: suspend test has duplicated lines (#10466)
  * ci: AppVeyor: do not install unibilium system-wide (#10464)
  * build: BuildLuv: set/pass WITH_LUA_ENGINE (#10449)
  * scripts/stripdecls.py #10458
  * build: LibUV: required version: 1.28.0 (#10456)
  * bundle: update libuv: v1.29.1 => v1.30.0 (#10365)
  * ui: add 'redrawdebug' option for flexible debugging of redrawing
  * compositor: handle float overlapping left half of doublewidth char
  * viml/reltime(): allow negative result #10453
  * eval.c: clang/"Dead assignment" #10446
  * Revert "tests: executable_spec: enable pending test #10443" (#10454)
  * window: allow resize wincmds for floats
  * tests: ex_terminal_spec: add test for previous leak (#10450)
  * ci: Travis: use minimum supported CMake in one job (#10445)
  * make all *.h linguist-language as C file #10442
  * CI: improve gcov handling #10404
  * api/window: add style="minimal" flag to nvim_open_win()
  * vim-patch:8.0.1164: changing StatusLine highlight does not always work
  * vim-patch:8.0.1146: redraw when highlight is set with same names
  * vim-patch:8.0.0755: terminal window does not have colors in the GUI
  * Fix lint failed
  * Fix errors
  * vim-patch:8.1.1611: bufadd() reuses existing buffer without a name
  * vim-patch:8.1.1610: there is no way to add or load a buffer without side effects
  * Change to not test msg_puts_pirntf() in unix CI
  * Change to use VV_PROGPATH instead os_exepath()
  * Add msg_puts_printf() test for multibyte characters
  * Fix problems with message catalog directory
  * Remove display_erros()
  * Remove USE_MCH_ERRMSG
  * Change mch_errmsg and mch_msg from macro to function
  * Add test for #7967
  * Fix garbled problem with msg_puts_printf on Windows
* Mon Aug 12 2019 Matej Cepl <mcepl@suse.com>
- Build on aarch64 and ppc64 requires a regular Lua, not LuaJIT
* Mon Aug 12 2019 Matej Cepl <mcepl@suse.com>
- The patch 10661.patch has been merged upstream, so it is
  unnecesary.
* Mon Aug 12 2019 Matej Cepl <mcepl@suse.com>
- Add batch new version of 10661.patch from
  https://github.com/neovim/neovim/pull/10661 allowing use just of
  - DLIBLUV_LIBRARY=/path/to/luv/luv.so as a parameter of cmake.
  Thank you, Daniel Hahler (@blueyed on GitHub), for the kind help.
* Sat Aug  3 2019 Matej Cepl <mcepl@suse.com>
- Remove unnecessary patch
* Sun Jul  7 2019 mcepl@cepl.eu
- Using ugly hack from
  https://github.com/neovim/neovim/issues/10407#issuecomment-517942811
  we are able to use luv.so directly.
- Update to version 0.4.0~git.1562515621.38342d75f:
  * ci: fix/improve Travis cache handling  [skip appveyor] (#10412)
  * tests: executable_spec: enable pending test #10443
  * build: fix GetCompileFlags for CMake #10444
  * func_clear_items: use XFREE_CLEAR #10436
  * vim-patch:8.1.1639: changing an autoload name into a file name is inefficient
  * vim-patch:8.1.1634: terminal test fails when term_getansicolors() is missing
  * vim-patch:8.1.1632: build with EXITFREE but without +arabic fails
  * vim-patch:8.1.1614: 'numberwidth' can only go up to 10
  * vim-patch:8.1.0229: crash when dumping profiling data #10428
  * termdebug.vim: vertical layout #10424
  * screen: disable redrawing inside VimResized
  * highlight: show "hi Group" message correctly when not using the screen
  * build: FindLibIntl: fix warning about CMP0075 (#10427)
  * BuildLuarocks: improve comments
  * BuildLuarocks.cmake: use ROCKS_DIR
  * .gitignore
  * tests: loop_spec: retry (#10413)
  * build: use -fdiagnostics-color=always with Ninja (#10419)
  * tests: fix flaky ':digraphs displays digraphs' (#10406)
  * build: FindLuaJit: handle luajit-2.1 include path suffix (#10418)
  * third-party: fix warning with (un)bundled libtermkey/unibilium (#10416)
  * win,fs.c: Fix is_executable_ext #10209
  * Improve luacheck setup  [skip appveyor]
  * Fix luacheck errors for all Lua source files
  * build: bundle: clean binary dir with new downloads (#10411)
  * tests: shell-test: add INTERACT mode (#10405)
  * tests: executable_spec: keep assertion (#10408)
* Wed Jul  3 2019 mcepl@cepl.eu
- Update to version 0.4.0~git.1562117839.e48257e63:
  * tests: fix/improve "TUI background color" tests (#10229)
  * ci: Travis: do not close fold on failure  [skip ci]
  * build: Fix rule of `build/.ran-third-party-cmake` #10402
  * tests: fix flaky "TermClose event triggers when fast-exiting terminal job stops" (#10377)
  * tests: fix flaky "terminal (with fake shell) with not arguments …" (#10401)
  * cmdline: remove local variables i and j from command_line_state
  * defaults: wildoptions=pum,tagfile #10384
  * test/old: pass  Test_recover_root_dir on Windows (#10207)
  * vim-patch:8.1.0452: MS-Windows: not finding intl.dll #10388
  * api/lua: make nvim_execute_lua use native lua floats, not special tables
  * cmdline: correct the column position of wildoptions=pum popupmenu
  * build: fix warning with passively available libintl (#10380)
  * build: LibLUV: update required version  [ci skip] (#10381)
  * fileio.c: eliminate set_file_time() #10357
  * man.vim: Handle ANSI escape sequences with ":" #10267
  * make vim.loop == require'luv'
  * libluv: use luv_set_callback to control callback execution
  * rename: FUNC_API_ASYNC => FUNC_API_FAST
  * :digraphs : check for CTRL-C less often #10376
  * Makefile: CMAKE_INSTALL_PREFIX: skip parsing CMAKE_EXTRA_FLAGS if set (#10374)
  * build: update cmake/LibFindMacros.cmake (#10355)
  * Makefile: move `all` target to the top  [ci skip] #10375
  * doc [ci skip] #10177
  * build: update some test dependencies (#10339)
  * build: FindLibLUV: use PkgConfig (#10359)
  * Makefile: revisit/improve checkprefix handling (#10348)
  * :ls : show "R", "F" for terminal-jobs #10370
  * build: CMake: do not set CMP0059 to old (#10363)
  * cmake/RunTests.cmake: fix TEST_TAG/TEST_FILTER  [ci skip] #10371
  * tests: fix flaky "timers can be stopped from the handler" (#10364)
  * viml/profile: switch to uv_gettimeofday() #10356
  * vim-patch:8.0.1259: search test can be flaky
  * vim-patch:8.0.1238: incremental search only shows one match
  * vim-patch:8.0.1202: :wall gives an errof for a terminal window
  * build: remove patch: luv-Add-missing-definitions-for-MinGW  [skip travis] #10360
  * build: CMake: remove usage of USE_BUNDLED_X in main project (#10354)
  * CMakeLists: remove/cleanup passing of CMAKE_SYSTEM_NAME (#10351)
  * build: BuildLua: fix check for mingw  [skip ci] (#10352)
  * ci: AppVeyor: GCOV_ERROR_FILE: head/tail  [skip ci] (#10335)
  * vim-patch:8.0.1120: :tm means :tmap instead of :tmenu
  * vim-patch:8.0.1100: stuck in redraw loop when 'lazyredraw' is set
  * vim-patch:8.0.1013: terminal window behaves different from a buffer with changes
  * vim-patch:8.0.0935: cannot recognize a terminal buffer in :ls output
  * Makefile: fix regression with "make functionaltest-lua" (#10346)
  * ci: Travis: upgrade OSX images (10.1 => 10.2) (#10319)
  * cmdline: remove invalid cmdline_show event when aborting mapping
  * compositor: handle scrolling of blended window
  * eval/api: don't allow the API to be called in the sandbox.
  * vim-patch:8.0.1688: some macros are used without a semicolon
  * vim-patch:8.1.1593: filetype not detected for C++ header files without extension
  * build: Makefile: fix distclean  [ci skip] (#10336)
  * api: make nvim__inspect_cell support multiple grids
  * ui: add 'winblend' to support blending of floating windows
  * build: use main cmake modules with third-party (#10330)
  * ci: revisit/fix coverage uploading (#10201)
  * vim-patch:8.1.1342: using freed memory when joining line with text property
  * vim-patch:8.0.1535: C syntax test still fails when using gvim
  * vim-patch:8.1.0198: there is no hint that syntax is disabled for 'redrawtime'
  * vim-patch:8.1.0437: may access freed memory when syntax HL times out
  * health.vim: check shada file #10327
  * build: CMake: remove LUAROCKS_VERSION (#10317)
  * lint
  * vim-patch:8.1.1401: misspelled mkspellmem as makespellmem
  * vim-patch:8.1.1382: error when editing test file
  * vim-patch:8.1.1368: modeline test fails with python but without pythonhome
  * vim-patch:8.1.1367: can set 'modelineexpr' in modeline
  * vim-patch:8.1.1366: using expressions in a modeline is unsafe
  * vim-patch:8.1.1365: source command doesn't check for the sandbox
  * build: luarocks: fall back to luajit (#10297)
  * tests: busted: do not use "--lua" (#10303)
  * vim-patch:8.0.1482: using feedkeys() does not work to test completion
  * os: close library even if uv_dlopen() fails
  * vim-patch:8.1.0347: some tests fail on Solaris
  * vim-patch:8.1.0086: no tests for libcall() and libcallnr()
  * vim-patch:8.0.1480: patch missing change
  * vim-patch:8.0.1479: insert mode completion state is confusing
  * build: Makefile: handle "rm -rf .deps" (#10305)
  * build: luajit: do not disable jit (#10318)
  * bundle: upgrade LuaJIT to latest v2.0 commit (#10320)
  * vim-patch:8.1.1055: CTRL-G U in Insert mode doesn't work for shift-Left
  * eval.c: Fix clint errors and typo in comment of ex_const()
  * vim-patch:8.1.1554: docs and tests for :const can be improved
  * vim-patch:8.1.1543: const test fails with small features
  * vim-patch:8.1.1539: not easy to define a variable and lock it
  * eval: assert VAR_LIST branch in filter_map()
  * getchar: Handle incomplete <Paste> in typeahead buffer #10311
  * vim-patch:8.1.0747: map() with a bad expression doesn't give an error
  * vim-patch:8.1.1519: 'backupskip' may contain duplicates
  * vim-patch:8.1.0853: options test fails on Mac
  * vim-patch:8.1.0850: test for 'backupskip' is not correct
  * vim-patch:8.1.0272: options test fails if temp var ends in slash
  * vim-patch:8.1.0270: checking for a Tab in a line could be faster
  * vim-patch:8.1.0242: Insert mode completion may use an invalid buffer pointer
  * vim-patch:8.1.0169: calling message_filtered() a bit too often
  * vim-patch:8.1.0167: lock flag in new dictitem is reset in many places
  * vim-patch:8.1.0166: using dict_add_nr_str() is clumsy
  * vim-patch:8.1.0165: :clist output can be very long
  * ops: refactor swapchar() to return bool
  * vim-patch:8.1.0125: virtual edit replace with multi-byte fails at end of line
  * vim-patch:8.1.0181: memory leak with trailing characters in skip expression
  * eval: require nonnull func args to pass ASAN build
  * vim-patch:8.1.0112: no error when using bad arguments with searchpair()
  * lint
  * vim-patch:8.0.1239: cannot use a lambda for the skip argument to searchpair()
  * screen: Adjust buffer sizes for multiple sign columns #10314
  * Makefile: fix trailing space in BUILD_CMD #10312
  * build: tests: build luv rock also with USE_BUNDLED_LUV=0 (#10307)
  * version.c: update [ci skip] #10115
  * tests: fix "api nvim_get_proc_children returns child process ids" (#10296)
  * tests: improve RunTests.cmake (#10239)
  * build: USE_BUNDLED_LUV=0 with USE_BUNDLED_LUAROCKS=1 #10291
  * cmake: fix usage of find_package_handle_standard_args (#10288)
  * CI/Travis: restore ASAN build to first stage #10274
  * CI: use -m to invoke pip #10275
  * Update argc(),argv() based on 8.1.0493
  * test/old: run test_arglist
  * vim-patch:8.1.0074: crash when running quickfix tests
  * vim-patch:8.1.0073: crash when autocommands call setloclist()
  * vim-patch:8.0.1726: older MSVC doesn't support declarations halfway a block
  * vim-patch:8.0.1723: using one item array size declaration is misleading
  * vim-patch:8.0.1274: setbufline() fails when using folding
  * vim-patch:8.0.1055: bufline test hangs on MS-Windows
  * vim-patch:8.0.1053: setline() does not work on startup
  * vim-patch:8.0.1039: cannot change a line in not current buffer
* Wed Jun 19 2019 mcepl@cepl.eu
- Update to version 0.4.0~git.1560900009.352d5a971:
  * ci: Travis: move gcov job to baseline (no allowed failures) (#10238)
  * tests: oldtests: mark Test_cursorhold_insert as flaky  [ci skip] (#10264)
  * ci: Travis: simplify/improve Python/pip setup  (#10228)
  * channel: refactor events, prevent recursive invocation of events
  * gcov: use __gcov_flush instead of __gcov_dump (#10260)
  * ci: Travis: skip lint job with "\[skip.lint\]"
  * ci: Travis: ccache: use --zero-stats
  * ci: AppVeyor: use fast_finish=true
  * ci/build.ps1: add comment for PATH mangling with old tests
  * ci: Travis: remove obsolete cmake file
  * ci/common/test.sh: fix some issues reported by shellcheck
  * vim-patch:8.1.1546: in some tests 'tags' is set but not restored
  * tests: fix Test_tagfiles: use Vim's 'tags' setting
  * vim-patch:8.0.1845: various comment updates needed, missing white space (#10203)
  * vim-patch:8.1.1003: playing back recorded key sequence mistakes key code (#10155)
  * messages: fix crash with msg_advance when using ext_messages
  * messages: support shortmess-=S in ext_messages
  * vim-patch:8.0.1549: various small problems in test files
  * vim-patch:8.0.1516: errors for job options are not very specific
  * vim-patch:8.1.0044: if a test function exists Vim this may go unnoticed
  * vim-patch:8.1.1545: when the screen is to small there is no message about that
  * ci: AppVeyor: ensure that win32 feature is set (#10216)
  * vim-patch:8.0.1245: when WaitFor() has a wrong expression it just waits a second (#10233)
  * ci: Travis: add baseline stage  [skip appveyor] (#10226)
  * ci: codecov: do not use flags  [ci skip] (#10227)
  * Dump gcov coverage in process_spawn (#10230)
  * api/lua: add on_detach to nvim_buf_attach
  * ci: AppVeyor: fix cov job, remove duplicate non-cov one (#10217)
  * vim-patch:8.0.0953: get "no write since last change" error in terminal window
  * test/old: pass Test_statusline on Windows
  * vim-patch:8.0.0933: terminal test tries to start GUI when it's not possible
  * vim-patch:8.0.0931: getwininfo() does not indicate a terminal window
  * tests: increase timeout with "timers doesn't mess up the cmdline" (#10212)
  * screen: showcmd should never move the cursor
* Thu Jun 13 2019 mcepl@cepl.eu
- Update to version 0.4.0~git.1560428451.cc4d463ca:
  * tui: support rgba background detection (#10205)
  * vim-patch:8.0.1704: 'backupskip' default doesn't work for Mac
  * tests: align tests in test_options to Vim (moved)
  * main: do event_init before early_init #10183
  * vim-patch:8.1.0213: CTRL-W CR does not work properly in a quickfix window
  * vim-patch:8.0.1689: no tests for xxd
  * vim-patch:8.1.1211: test user command code #10162
  * adjust tests for nvim
  * vim-patch:8.1.1292: invalid command line arguments not tested
  * local.mk.example: add example for -Werror  [ci skip] #10178
  * TUI: set os/input.c:global_fd to input->in_fd #10174
  * doc [ci skip] #10129
  * lua: introduce vim.loop (expose libuv event-loop) #10123
  * vim-patch:8.0.1278: Add the "k" flag in 'guioptions' #10175
  * lint
  * vim-patch:8.1.1509: cmdline_row can become negative, causing a crash
  * vim-patch:8.0.1756: GUI: after prompting for a number the mouse shape is wrong
  * search_stat: show "??/?" dual in right-to-left case #10170
  * vim-patch.sh: git-for-each-ref: use strip  [ci skip] #10169
  * vim-patch.sh: improve performance with -l  [ci skip] #10165
  * vim-patch:8.0.1305: writefile() never calls fsync() #10153
  * vim-patch:8.1.1191: test debug commands #10158
  * vim-patch:8.1.0769: :stop is covered in two tests #10157
  * vim-patch:8.1.1491: fix skipping after exception #10164
  * vim-patch:8.1.0131: :profdel is not tested
  * vim-patch:8.1.0130: ":profdel func" does not work if func was called already
  * vim-patch:8.1.0426: accessing invalid memory in SmcOpenConnection()
  * test/old: ignore defaults.vim assertion
  * vim-patch:8.1.0417: several command line arguments are not tested
  * vim-patch:8.1.0409: startup test fails on MS-Windows
  * vim-patch:8.1.0406: several command line arguments are not tested
  * vim-patch.sh: use --no-backup-if-mismatch [ci skip] #10156
  * vim-patch:8.1.0830: test leaves directory behind #10152
  * vim-patch:8.1.1199: no test for :abclear #9936
  * vim-patch.sh: improve patching [ci skip] #10154
  * vim-patch.sh: improve performance #10137
  * vim-patch.sh: fix shellcheck issues  [ci skip] #10138
  * vim-patch:8.1.0813: FileChangedShell not sufficiently tested
  * vim-patch:8.1.0807: session test fails on MS-Windows
  * vim-patch:8.1.0529: flaky test sometimes fails in different ways
  * vim-patch:8.1.0430: Xargadd file left behind after running test
  * vim-patch:1ebff3dc9 #10144
  * Test_writefile_sync_dev_stdout: use s for sync explicitly
  * vim-patch:9980b37a80
  * vim-patch:83799a7b7
  * defaults: exclude "S" from 'shortmess' #10136
  * vim-patch:8.0.1702: leaking memory when autocommands make quickfix list invalid
  * vim-patch:8.1.0060: crash when autocommands delete the current buffer
  * vim-patch:8.0.1784: gvim test gets stuck in dialog
  * vim-patch:8.0.1669: :vimgrep may add entries to the wrong quickfix list
  * vim-patch:8.0.1414: accessing freed memory in :lfile.
  * vim-patch:8.0.1412: using free memory using setloclist()
  * vim-patch:8.0.1384: not enough quickfix help; confusing winid
  * vim-patch:8.1.1475: search string not displayed when 'rightleft' is set
  * vim-patch:8.1.1375: without "TS" in 'shortmess' get a hit-enter prompt often
  * vim-patch:8.1.1390: search stats are off when using count or offset
  * vim-patch:8.1.1350: "W" for wrapping not shown when more than 99 matches
  * vim-patch:8.1.1289: may not have enough space to add "W" to search stats
  * vim-patch:8.1.1288: search stats don't show for mapped command
  * vim-patch:8.1.1283: delaying half a second after the top-bot message
  * vim-patch:8.1.1271: compiler warnings for use of STRNCPY()
  * vim-patch:8.1.1270: cannot see current match position
  * vim-patch:8.1.0629: "gn" selects the wrong text with a multi-line match
* Sat Jun  8 2019 Matej Cepl <mcepl@suse.com>
- Return set_version back
* Thu Jun  6 2019 mcepl@cepl.eu
- Update to version 0.4.0~git.1559813723.8e8c7d754:
  * vim-patch:8.1.1470: new doublewidth Unicode character U32FF #10126
  * lua: docs and tests for vim.schedule
  * lua: add vim.schedule(cb)
  * normal: Don't exit CTRL-O mode after processing K_EVENT
  * api: allow nvim_buf_attach from lua using callbacks
  * version.c: update [ci skip] #10072
  * vim-patch:8.1.0002: :stopinsert changes the message position
  * vim-patch:8.1.0804: crash when setting v:errmsg to empty list
  * vim-patch:8.0.1518: error messages suppressed after ":silent! try"
  * main.c: Change to use redraw_later(VALID)
  * Fix issue where test fails
  * [skip appveyor] Fix clint issue
  * main.c: Change TUI to initialize like GUI
  * tui/input.c: Fix problem when stdin is not TTY
  * main.c: fixes #7967
  * msg_puts_attr_len: check default_grid.chars if headless
  * Fix screenchar() problem in headless mode
  * api/buffer: create new buffers in the "opened" state
  * test: don't detach screen just to change the size
  * Add test
  * Fix multiple c_CTRL-D showing statusline
  * oldtests: set laststatus=1
  * functionaltests: fix new execute() tests
  * update functional test for "places cursor correctly #6035"
  * UI: Fix wrong msg_col after execute()
  * vim-patch:8.1.0571: non-silent execute() resets display column to zero
  * vim-patch:8.1.0569: execute() always resets display column to zero
  * build: fix some warnings
  * test: avoid some boilerplate
  * Make sure msg_clear is sent after confirm message (#10065)
  * [RDY] Fix wildmode=list,full and display+=msgsep interaction (#10103)
  * deps: update to libuv v1.29.1
  * test: cleanup, reduce verbosity
  * doc [ci skip] #10097
  * signs: fix crash in buf_addsign #10091
  * vim-patch:8.1.1436: writefile test fails when run under /tmp
  * lint
  * vim-patch:8.1.1000: indenting is off
  * vim-patch:8.1.1114: confusing overloaded operator "." for string concatenation
  * lint
  * vim-patch:8.1.0902: incomplete set of assignment operators
  * vim-patch:8.0.0785: wildcards are not expanded for :terminal
  * vim-patch:8.1.1411: fix divide by zero #10073
  * version.c: update [ci skip] (#9875)
* Mon May 27 2019 mcepl@cepl.eu
- Update to version 0.4.0~git.1558951295.69b3d5acd:
  * lint
  * vim-patch:8.1.1077: reg_executing() is reset by calling input()
  * vim-patch:8.1.0995: a getchar() call resets the reg_executing() result
  * vim-patch:8.1.0020: cannot tell whether a register is executing or recording
  * UI/ext_messages: restore kind=quickfix #10067
  * UI/cmdline: check if redraw is needed after K_EVENT, K_COMMAND #9804
  * lint
  * Skipping Test_sign_memfailures (unsupported memory checks)
  * Fix out of bounds read in sign_group_ref
  * vim-patch:8.1.0039: cannot easily delete lines in another buffer
  * Resolved compile warnings & fixed lot of style related to sign api
  * Allow multiple signs of same type in one line (matching vim behaviour)
  * Fixed ordering of signs to align vim and neovim behaviour
  * Changed sign_mark_adjust behaviour to match vim
  * vim-patch:8.1.0772: the sign_define_by_name() function is too long
  * vim-patch:8.1.0767: when deleting lines at the bottom signs are misplaced
  * vim-patch:8.1.0750: when the last sign is deleted the signcolumn may remain
  * vim-patch:8.1.0717: there is no function for the ":sign jump" command
  * vim-patch:8.1.0709: windows are updated for every added/deleted sign
  * vim-patch:8.1.0702: ":sign place" only uses the current buffer
  * vim-patch:8.1.0701: sign message not translated and inconsistent spacing
  * vim-patch:8.1.0697: ":sign place" requires the buffer argument
  * vim-patch:8.1.0679: sign functions do not take buffer argument as documented
  * vim-patch:8.1.0673: functionality for signs is spread out over several files
  * vim-patch:8.1.0669: the ex_sign() function is too long
  * vim-patch:8.1.0660: sign_cleanup() may leak memory
  * vim-patch:8.1.0658: deleting signs and completion for :sign is insufficient
  * vim-patch:8.1.0644: finding next sign ID is inefficient
  * vim-patch:8.1.0632: using sign group names is inefficient
  * vim-patch:8.1.0614: placing signs can be complicated
  * doc/API: document indexing behavior #10058
  * messages: use proper multiline error message for rpcrequest and API wrappers
  * lint
  * vim-patch:8.1.0307: there is no good way to get the window layout
  * vim-patch:8.1.0211: expanding a file name "~" results in $HOME
  * test/old: remove duplicates, run test_tabpage.vim
  * vim-patch:8.1.0751: some regexp errors are not tested
  * vim-patch:8.1.0547: modeline test with keymap still fails
  * vim-patch:8.1.0546: modeline test with keymap fails
  * vim-patch:8.1.0506: modeline test fails when run by root
  * vim-patch:8.1.0206: duplicate test function name
  * vim-patch:8.1.0205: invalid memory access with invalid modeline
  * vim-patch:8.1.0817: test ":=" command #10062
  * Fix memfile_test.c path
  * vim-patch:8.1.0317: Cscope test fails when using shadow directory
  * vim-patch:8.1.0188: no test for ":cscope add"
  * Allow 3 beeps per half a second
  * clint: remove CheckAltTokens()
  * lint
  * vim-patch:8.0.0683: visual bell flashes too quickly
  * kvec.h: kv_destroy: reinitialize after free
  * vim-patch:8.0.1496: VIM_CLEAR()
  * refactor: introduce XFREE_CLEAR()
  * doc #10017
  * vim-patch:8.1.1171: statusline test could fail in large terminal
  * vim-patch:8.0.1220: skipping empty statusline groups is not correct
  * vim-patch:8.0.1208: 'statusline' drops empty group with highlight change
  * lint
  * vim-patch:8.1.1373: "[p" in Visual mode puts in wrong line
  * vim-patch:8.1.1363: ":vert options" #10048
  * vim-patch:8.1.0293: checks for type of stack is cryptic
  * cleanup: remove HAVE_SELINUX #10040
  * vim-patch:8.1.1360: buffer left 'nomodifiable' after :substitute
  * vim-patch:8.0.1519: getchangelist() does not use argument as bufname()
  * lua/shared: share trim() impl
  * fileio: set group of backup file
  * vim-patch:8.0.1514: getting the list of changes is not easy
  * runtime/termdebug.vim: handle "\n" as linebreaks #10037
  * vim-patch:8.1.1358: cannot enter character with a CSI byte
  * vim-patch:8.1.1357: test 37 is old style
  * lint
  * vim-patch:8.1.0901: index in getjumplist() may be wrong
  * vim-patch:8.0.1513: the jumplist is not always properly cleaned up
  * vim-patch:8.0.1498: getjumplist() returns duplicate entries
  * vim-patch:8.0.1497: getting the jump list requires parsing the output of :jumps
  * vim-patch:8.0.1082: tests fail when run under valgrind
  * eval.c: add has("osx") for apple
  * vim-patch:8.1.1353: undo test fails on Mac
  * lint
  * vim-patch:8.1.1352: undofile() reports wrong name
  * lua/shared: share more stuff
  * lua/shared: share deepcopy() with test/*
  * gen_vimdoc.py: support lua/shared.lua module [ci skip]
  * Document the vim.lua functions
  * gen_vimdoc.py: get Lua docs via lua2dox.lua #9740
  * lua/shared: move table util funcs to vim.shared
  * genappimage.sh: migrate to linuxdeploy #10027
  * vim-patch:8.1.1349: if writing runs into conversion error backup file is deleted
  * vim-patch:8.1.1348: running tests may cause the window to move
  * vim-patch:8.1.1325: cannot build with +eval but without +channel and +timers
  * vim-patch:8.1.1345: stuck in sandbox with ":s/../\=Function/gn"
  * kbtree.h: assert valid range #10022
  * test: remove use of require('test.helpers')
  * test: share implementation of testdir/load.vim
  * lua/stdlib: Introduce vim.shared
  * test: Extend {unit,functional}.helpers with global helpers
  * kbtree: pointer UB and unitialized value fixes
  * vim-patch:8.1.1338: fix hang when concealing wide char #10023
  * runtime/termdebug.vim #10015
  * runtime/termdebug.vim #8364
  * ui/terminal: make terminal state redraw like any other state
  * autocmd: fixes and tests for autocmd window issues
  * API/nvim_set_keymap: remove mode-shortname aliases
  * API/nvim_set_keymap: minor cleanup
  * docs: explicitly state return value on success
  * test: move trim to global helpers
  * test: make first attempt at some kind of test
  * style: make linter happy with fileio.c
  * fs: add UV_FS_COPYFILE_FICLONE flag to os_copy
  * fs: remove unecessary copybuf and os_open call
  * fs: replace another custom copy with os_copy
  * fs: add os_copy function that uses uv_fs_copyfile
* Thu May 16 2019 mcepl@cepl.eu
- Update to version 0.4.0~git.1557998465.3a699a790:
  * runtime/termdebug.vim #8364
  * ui/terminal: make terminal state redraw like any other state
  * autocmd: fixes and tests for autocmd window issues
  * API/nvim_set_keymap: remove mode-shortname aliases
  * API/nvim_set_keymap: minor cleanup
- Remove neovim-termdebug-PR8364.patch as it has been merged
  upstream.
* Sun May 12 2019 mcepl@cepl.eu
- Add neovim-termdebug-PR8364.patch for suggested fix for gh#neovim/neovim#8364
- Update to version 0.4.0~git.1557654288.fbf2c414a:
  * API: nvim_set_keymap, nvim_del_keymap #9924
  * test/channels_spec: cleanup
  * doc
  * UI/ext_messages: learn more message kinds
  * vim-patch:8.1.0543: fix memory leak #10001
  * vim-patch:8.1.1312: Coverity warning for using uninitialized variable
  * vim-patch:8.1.1306: Borland support is outdated and doesn't work
  * runtime/tutor [ci skip] #9990
  * UI/nvim_ui_attach(): add `override` option
  * vim-patch:8.1.1299: "extends" from 'listchars' is used when 'list' is off
  * vim-patch:8.1.0865: when 'listchars' only contains "nbsp:X" it does not work
  * vim-patch:8.1.1205: BufReadPre may move the cursor #9980
  * vim-patch:8.1.1293: MSVC files are no longer useful #9982
  * vim-patch:8.0.1144: using wrong #ifdef for computing length
  * lint
  * vim-patch:8.1.0133: tagfiles() can have duplicate entries
  * API: fix cursor position when lines are added #9961
  * vim-patch:8.0.0876: backslashes and wildcards in backticks don't work
  * fixup! vim-patch:8.0.1782: no simple way to label quickfix entries
  * vim-patch:8.1.1284: detecting *.tmpl as htmlcheetah is outdated
  * vim-patch:8.1.1286: running tests leaves XTest_tabpage_cmdheight file behind
  * vim-patch:8.1.1285: test17 is old style
  * appdata: Include more info #9974
  * aucmd_win: use a floating window
  * lint
  * PVS/V781: "maxlen" variable checked after use
  * PVS/V547: Expression is always true
  * PVS/V547: Expression is always false
  * PVS/V547: Expression is always false
  * PVS/V571: condition was already verified
  * vim-patch:8.0.1750: crash clearing location list #9968
  * test: cleanup
  * vim-patch:8.1.1046: the "secure" variable is used inconsistently
  * vim-patch:8.1.0613: when executing an insecure function the secure flag is stuck
  * lint
  * doc: update setqflist()
  * tests: adjust to latest Vim patches
  * vim-patch:8.0.1831: sometimes the quickfix title is incorrectly prefixed with ':'
  * vim-patch:8.0.1805: qf_parse_line() is too long
  * vim-patch:8.0.1782: no simple way to label quickfix entries
  * vim-patch:8.0.1727: qf_get_properties() function is too long
  * vim-patch:8.0.1678: errorformat "%%r" implies "%%>"
  * vim-patch:8.0.1634: the ex_vimgrep() function is too long
  * vim-patch:8.0.1569: warning for uninitialized variable from gcc
  * test/old: set shellslash in Test_finddir
  * test/old: enable Test_normal01_keymodel
  * vim-patch:8.1.1249: compiler warning for uninitialized variable
  * vim-patch:8.0.1500: possible NULL pointer dereference
  * vim-patch:8.0.1432: after ":copen" can't get the window-ID of the quickfix window
  * vim-patch:8.0.1420: accessing freed memory in vimgrep
  * vim-patch:8.0.1406: difficult to track changes to a quickfix list
  * vim-patch:8.0.1389: getqflist() items are missing if not set
  * vim-patch:8.0.1353: QuickFixCmdPost is not used consistently
  * vim-patch:8.1.0369: continuation lines cannot contain comments
  * vim-patch:8.0.1708: mkdir with 'p' flag fails on existing directory
  * lint
  * vim-patch:8.1.1242: no cmdline redraw when tabpages have different 'cmdheight'
  * vim-patch:8.1.0794: white space before " -Ntabmove" causes problems
  * terminal.c: remove unnecessary macro
  * terminal: swap priority of terminal, editor highlights
  * ex_getln: fix statusline redraw logic #9967
  * gen_vimdoc.py: support <pre> preformatted text [ci skip]
  * doc [ci skip]
  * lint
  * vim-patch:8.0.1267: Test_swap_group may leave file behind
  * vim-patch:8.0.1265: swap test not skipped when there is one group
  * vim-patch:8.0.1263: others can read the swap file if a user is careless
  * vim-patch:8.1.0642: swapinfo() leaks memory
  * lint
  * vim-patch:8.1.1234: swap file test fails on MS-Windows
  * test/old: skip Test_swapfile_delete() until "blob" is merged
  * verb_msg: remove char_u
  * vim-patch:8.1.1231: asking about existing swap file unnecessarily
  * vim-patch:8.1.0401: can't get swap name of another buffer
  * vim-patch:8.1.0325: strings in swap file may not be NUL terminated
  * vim-patch:8.1.0316: swapinfo() test fails on Travis
  * vim-patch:8.1.0314: add swapinfo() "dirty" item
  * vim-patch:8.1.0313: information about a swap file is unavailable
  * vim-patch:8.0.1563: getwinposx() timeout #9955
  * clipboard: setreg("*") with clipboard=unnamed #9954
  * lint
  * vim-patch:8.1.0843: memory leak when running "make test_cd" #9944
  * tui:cursor_goto(): remove dead code #9952
  * runtime/Tutor: define highlights as "default" #9947
  * vim-patch:8.1.0519: cannot save and restore the tag stack
  * win: stream_init() issue with tty on Windows #9884
  * test/old: remove test16 (#9949)
  * win/defaults: Use "…/nvim-data/site" in 'runtimepath'
  * vim-patch:8.1.1214: old style tests #9948
  * spellfile.vim: store files in stdpath('data')
  * doc/API #9916
  * test: clear(): remove `opts.headless` parameter
  * test: clear(): `args_rm` parameter
  * test: 'shadafile' default
  * test/old: remove test.out files
  * vim-patch:8.1.1209: clever compiler warns for buffer being too small
  * vim-patch:8.1.1207: some compilers give warning messages
  * vim-patch:8.1.1180: Vim script debugger tests are old style
  * oldtests: pass Test_ReadWrite_Autocmds()
  * vim-patch:8.1.1203: some autocmd tests are old style
  * vim-patch:8.1.1194: typos and small problems in source files
  * vim-patch:8.1.0837: timer interrupting cursorhold and mapping not tested
  * vim-patch:8.0.1510: cannot assert beep #9938
  * Spurious quote mark in command line when typing <C-R> (#9934)
  * vim-patch:8.0.1408: crash in setqflist()
  * vim-patch:8.0.0768: terminal window status shows "[Scratch]"
  * vim-patch:8.0.0797: finished job in terminal window is not handled
  * vim-patch:8.0.1133: syntax timeout not used correctly
  * vim-patch:8.0.1107: terminal debugger jumps to non-existing file
  * vim-patch:8.0.1092: terminal debugger can't evaluate expressions
  * vim-patch:8.0.1085: terminal debugger can't set breakpoints
  * lint
  * vim-patch:8.0.0647: syntax highlighting can make cause a freeze
  * gen_vimdoc.py: skip "Parameters" header if all excluded
  * health/provider.vim: check curl HTTPS support
  * doc: clarify -Es
  * doc: UI
  * doc
  * health: check if tmux enabled true colors (#9929)
  * Reset stop_insert_mode in terminal_enter rather than terminal_check
  * vim-patch:8.1.1177: .ts files are recognized as xml, typescript is more common (#9922)
  * options: avoid using empty 'shadafile'
  * vim-patch:8.0.0716: "--clean", 'shadafile' #9907
  * vim-patch:8.0.1112: can't get size or current index from quickfix list
  * vim-patch:8.0.1093: various small quickfix issues
  * vim-patch:8.0.0776: function prototypes missing without the quickfix feature
  * vim-patch:8.0.0761: options not set properly for a terminal buffer
  * Build gperf with configured host compiler.
  * Set host C++ compiler CMake var.
  * windows: float config changes
  * inccommand: Disable K_EVENT during preview calculation
  * inccommand: Ignore :redraw during preview
  * chdir: remove unused argument #9901
  * vim-patch:8.0.1130: the qf_jump() function is still too long
  * vim-patch:8.0.1104: the qf_jump() function is too long
  * generators: fix filename typo in help message
  * API: emit nvim_error_event on failed async request
  * options: properly reset directories on 'autochdir' (#9894)
  * lint
  * vim-patch:8.1.1157: Unicode tables are out of date
  * vim-patch:8.1.1156: Unicode emoji and other image characters not recognized
* Fri Apr 12 2019 mcepl@cepl.eu
- Update to version 0.4.0~git.1555078441.d08692a82:
  * options: comma-separated options don't allow duplicates (#9891)
  * vim-patch:8.0.0714: cmdline redraw during timer #9835
  * RPC: conform message-id type to msgpack-RPC spec
  * RPC: eliminate NO_RESPONSE
  * PVS/V595: pointer utilized before checking NULL
  * vim-patch.sh: perf, readability #9044
  * float: always change to valid windows (#9878)
  * ops: use ARRAY_SIZE macro for opchars array length
  * vim-patch:8.0.1411: reading invalid memory with CTRL-W :
  * vim-patch:8.0.0725: a terminal window does not handle keyboard input
  * vim-patch:8.1.1140: not easy to find out what neighbors a window has (#9873)
  * startup: -es/-Es (silent/batch mode): skip swapfile #8540
  * version.c: update [ci skip]
  * vim-patch:8.0.0702: error in a timer can make Vim unusable #9826
  * ci/build.ps1: Respect CMAKE_BUILD_TYPE if provided #9869
  * vim-patch:8.1.1118: a couple of conditions are hard to understand
  * vim-patch:8.1.1134: buffer for quickfix window is reused for another file
  * vim-patch:8.0.1763: :argedit does not reuse an empty unnamed buffer
  * lint
  * Remove MSVC optimization workaround for SHM_ALL
  * api/window: validate cursor in nvim_win_set_buf
  * doc: rewrite *feature-list*
  * doc [ci skip]
  * event-loop: do not set CA_COMMAND_BUSY #9853
  * Make SHM_ALL to a variable instead of a compound literal #define
  * CI/AppVeyor: remove redundant cache directive
  * CI/AppVeyor: do not cache pacman packages
  * CI/AppVeyor: print info about restored cache
  * :stopinsert should leave terminal-mode #9856
  * CI/AppVeyor: build deps out-of-tree
  * CI/AppVeyor: do skip-logic earlier #9854
  * CI/AppVeyor: per-compiler deps cache #9852
  * build: fix warning
  * vim-patch:8.1.1123: avoid filtering autocomplete
  * vim-patch:8.1.1113: making an autocommand trigger once is not so easy
  * vim-patch:8.0.0728: the terminal structure is never freed
  * oldtests: win: filename cannot have "
  * oldtests: set shellslash for ":cd" test
  * vim-patch:8.1.0308: a quick undo shows "1 seconds ago"
  * vim-patch:8.1.0135: undo message delays screen update for CTRL-O u
  * vim-patch:8.0.0709: libvterm cannot use vsnprintf()
  * vim-patch:8.1.0494: functions do not check for a window ID in other tabs
  * vim-patch:8.1.0493: argv() and argc() only work on the current argument list
  * vim-patch:8.1.0218: cannot add matches to another window
  * coverity/183543: Null pointer dereference #9836
  * vim-patch:8.1.1072: extending sign and foldcolumn below the text is confusing (#9816)
  * vim-patch:8.1.1100: tag file without trailing newline no longer works
  * vim-patch:8.1.1094: long line in tags file causes error
  * vim-patch:8.1.1093: support for outdated tags format slows down tag parsing
  * lint
  * oldtests: set shellslash for Test_non_zero_arg
  * vim-patch:8.1.0119: failing test goes unnoticed because messages is not written
  * vim-patch:8.1.0118: duplicate error message for put command
  * vim-patch:8.0.0681: unnamed register only contains the last deleted text
  * test: "$PATHEXT=::"
  * jumplist: avoid extra tail entry #9805
  * fs.c: fix is_executable_ext()
  * [ci skip] fs.c: fix comment
  * fs.c: Move sh check of is_executable_ext to outside of loop
  * fs.c: Simplify calling is_executable_ext
  * test/win: Remove unnecessary set shell
  * fs.c: fix is_executable_ext
  * fs.c: eliminate is_extension_executable
  * is_extension_executable: simplify check for unix-style shell
  * is_extension_executable: simplify
  * cleanup: PATHEXT function
  * test/win: executable(), exepath() #9516
  * win: exepath(): append extension if omitted
  * PVS/V560: expression is always true
  * clang/"null pointer dereference": insert_execute
  * clang/"result is garbage/undefined": win_close
  * win: executable(): also check extension
  * win: executable(): fix relative path bug
  * keymap, terminal: more keycodes #9810
  * vim-patch:8.1.1087: tag stack is incorrect after CTRL-T and then :tag
  * vim-patch:8.1.1082: "Conceal" match is mixed up with 'hlsearch' match.
  * vim-patch:8.1.1074: Python test doesn't wipe out hidden buffer
  * vim-patch:8.1.1073: space in number column is on wrong side with 'rightleft' set
  * eval: diff_hlID() and hlID() return same id
  * vim-patch:8.0.1153: no tests for diff_hlID() and diff_filler()
  * vim-patch:8.1.1095: win: executable() on very long name #9820
  * autocmd: rename MenuPopupChanged to CompleteChanged #9819
  * vim-patch:8.0.0705: check did_throw before discarding exception #9808
  * vim-patch:8.1.1088: height of quickfix window not retained with vertical split (#9818)
  * vim-patch:8.0.0629: set `starting` earlier
  * complete_info(): fix null reference
  * vim-patch:8.1.0045: popup test isn't run completely
  * vim-patch:8.1.1068: cannot get all the information about current completion
  * cursormoved: add tests for CursorMoved
  * cursormoved: always trigger CursorMoved when entering window
  * cursormoved: make global last_cursormoved window-local
  * fixup: use vim_snprintf, ASCII_ISALNUM
  * lint
  * keymap: add more (keypad) keycodes #9793
  * vim-patch:8.1.0544: setting 'filetype' in a modeline causes an error
  * vim-patch:8.1.0540: may evaluate insecure value when appending to option
  * vim-patch:8.1.0539: cannot build without the sandbox
  * gen_ex_cmds.lua: build the command table
  * vim-patch:8.0.0506: can't build with ANSI C
  * vim-patch:8.0.0504: looking up an Ex command is a bit slow
  * vim-patch:8.1.1061: when substitute string throws error, substitute happens anyway
  * vim-patch:8.1.0887: the 'l' flag in :subsitute is sticky
  * vim-patch:8.1.0528: various typos in comments
  * vim-patch:8.0.1528: dead code found
  * gen_help_html.py [ci skip]
  * doc, lint
  * gen_vimdoc.py: render nested lists, etc [ci skip]
  * doc: mention "pynvim" module rename
  * doc: move ui-wildmenu to deprecated.txt [ci skip]
  * doc [ci skip]
  * mac: do not use libintl_setlocale() (#9789)
  * tui/input.c: rename functions
  * signs: support multiple columns #9295
  * Update to restore layout only for non-floating windows
  * Update test
  * floating-window.c: fix crash when using inccommand
  * window: don't crash when closing two floats in a row
  * vim-patch:8.1.1045: E315 ml_get error when using Python and hidden buffer
  * vim-patch:8.1.0538: evaluating a modeline might invoke using a shell command
  * vim-patch:8.1.0189: function defined in sandbox not tested
  * vim-patch:8.1.0177: defining function in sandbox is inconsistent
  * help: ignore snapshotted window if invalid (#9774)
  * api: ignore floating windows for laststatus=1 (#9771)
  * vim-patch:8.1.1026: unused condition
  * vim-patch:8.1.1025: checking NULL pointer after addition
  * :mksession : restore tab-local working directories #9754
  * doc #9751
  * test: add more debuggings tips [ci skip] (#9761)
  * vim-patch:8.1.0384: sign ordering #9758
  * vim-patch:8.1.{0849,1001}: 'cursorline' highlight #9757
  * build: do not pass empty CMAKE_INSTALL_PREFIX
  * test: example_spec.lua
  * vim-patch:8.1.0775: matching too many files as zsh
  * vim-patch:8.1.0771: some shell filetype patterns end in a star
  * vim-patch:8.1.1017: off-by-one error in filetype detection
  * build: pass CMAKE_INSTALL_PREFIX explicitly #9748
  * vim-patch:8.1.0048: vim_str2nr() on numbers close to max #9744
  * oldtests: use LoadAdjust() on timer test
  * vim-patch:8.1.0858: 'indentkeys' and 'cinkeys' defaults are different
  * cmdline: revert <down> and <up> mappings for wildoptions=pum
  * aucmd_prepbuf: also restore `prevwin` #9741
  * vim-patch:8.1.1011: indent from autoindent not removed #9742
  * clipboard: Always copy as plain text in Wayland #9737
  * api: add tests for new code paths
  * Allow using internal popupmenu or ext_popupmenu for wildmenu
  * oldtests: wait 200ms on mac for timer test
  * api: refactor FloatRelative usage
  * api: numerous small fixes
  * api: update doc
  * api: add width/height to FloatConfig
  * api: nvim_win_config() -> nvim_win_set_config()
  * api: refactor FloatAnchor usage
  * api: add nvim_win_get_config()
  * vim-patch:8.1.0019: error when defining a Lambda with index of a function result
  * test: simplify TUI bg-detection test
  * vim-patch:8.1.0728: avoid breaking after single space #9733
  * autocmd: add MenuPopupChanged autocmd
  * vim-patch:8.1.0671: cursor in wrong column after auto-format #9729
  * compositor: fix rendering issues with floats opened after popupmenu
  * autocmd: do not show empty section after ++once handlers expire
  * autocmd: rename: "++nested", "++once"
  * vim-patch:8.0.1447: still too many old style tests (#9725)
  * dictwatcheradd(): support b:changedtick #9693
  * TextYankPost: add v:event["inclusive"] #9717
  * vim-patch:8.1.0170: invalid memory use with complicated pattern #9724
  * test/CI: skip "throttles output" test on Travis macOS #9721
  * docs: adjust the generated nvim_open_win docs
  * docs: update generated API docs
  * docs: floating windows introduction
  * floats: add NormalFloat highlight and 'nonumber' default
  * window: simplify logic for entering new float
  * autocmd: rename "once" => "-once" #9713
  * Dist: make icon a proper square (#9716)
  * TUI/background detection: hook into VimEnter event
  * cleanup: rename menu_nable_recurse() #9707
  * autocmd: introduce "once" feature
  * vim-patch:8.1.1002: "gf" on URL with port number #9705
  * executable(): return false if user is not owner #9703
  * vim-patch:8.1.0994: fix relative cursor position #9676
  * floating-window: fix crash setting cmdheight #9685
  * vim-patch:8.0.1372: profile log may be truncated halfway a character
  * vim-patch:8.1.0826: too many #ifdefs
  * oldtests: set shellslash in Test_true_false_arg()
  * oldtests: set shellslash in Test_shellescape()
  * vim-patch:8.1.0739: text objects in not sufficiently tested
  * vim-patch:8.1.0998: getcurpos() unexpectedly changes "curswant"
  * lint: fix coding style
  * vim-patch:8.0.0646: the hlsearch test fails on fast systems
  * vim-patch:8.0.0645: no error for illegal back reference in NFA engine
  * vim-patch:8.0.0644: the timeout for 'hlsearch' is not tested
  * vim-patch:8.0.0643: when a pattern search is slow Vim becomes unusable
  * vim-patch:8.1.0935: old regexp engine may use invalid buffer #9692
  * tui_tk_ti_getstr: handle weird value #9688
  * Fix os.getenv of lua on Windows
  * Fix environment variable on Windows
  * PVS/V560: window.c: fix always true condition #9682
  * buffer: use aucmd_prepbuf() instead of switch_to_win_for_buf()
  * vim-patch:8.1.0875: not all errors of marks and findfile()/finddir() are tested
  * vim-patch:8.1.0891: substitute command inssuficiently tested
  * PVS/V501: ui_compositor.c: identical sub-expressions #9673
  * edit.c: Disable indent during completion
  * api: add nvim_win_close() to close window by id
  * test: multibyte env var names #9655
  * os/env: Fix completion of multibyte env var names
  * vim-patch:8.1.0971: failure to select quoted text obj moves cursor #9658
  * floats: implement floating windows
  * ops.c: do_join expects `count` of 2 or greater #6855
  * vim-patch.sh: mention URL for `hub` tool #9659
  * search.c: remove dead code #5307
  * cleanup: remove legacy `enc_dbcs` global #9660
  * screen.c: remove dead code #6609
  * API/buffer-updates: always detach on buf-reload #9643
  * os: remove uv_translate_sys_error impl #9652
  * vim-patch:8.1.0973: pattern with syntax error gives threee error messages
  * vim-patch:8.1.0965: search test fails
  * vim-patch:8.1.0963: illegal memory access when using 'incsearch'
  * vim-patch:8.1.0968: crash when using search pattern \%%Ufffffc23
  * test: fix isCI() for Quickbuild
  * test/env: multibyte env var to child process
  * clint: check env functions
  * vim-patch:8.1.0985: crash with large number in regexp
  * os/env: use libuv v1.12 getenv/setenv API
  * os_getenv, os_setenv: revert "widechar" impl
  * win: os_getenv(): use _wgetenv()
  * utf16_to_utf8: minor fixes
  * os_setenv: use _wputenv_s; remove vestigial code #7920
  * TUI: do not resize host-terminal on startup (#9645)
  * vim-patch:8.1.0980: extend() insufficiently tested (#9646)
  * vim-patch:8.1.0225: mode() does not indicate using CTRL-O from Insert mode (#9644)
  * vim-patch:8.1.0959: sorting large numbers is not tested (#9641)
  * TUI: rework background-color detection
  * third-party: libtermkey v0.20 -> v0.21.1
  * win/deps: update to (forked) libuv v1.26.0
  * I/O: ignore ENOTSUP for failed fsync()
  * deps: update to libuv v1.26.0
  * fix "E667: Fsync failed" on macOS
  * man.vim: g:man_hardwrap #9633
  * vim-patch:8.1.0276: no test for 'incsearch' highlighting with :s
  * vim-patch:8.1.0387: no test for 'ambiwidth' detection
  * vim-patch:8.1.0668: no test for overstrike mode in the command line
  * vim-patch:8.1.0937: invalid memory access in search pattern
  * vim-patch:8.1.0934: invalid memory access in search pattern
  * vim-patch:8.1.0926: no test for :wnext, :wNext and :wprevious
  * lint
  * vim-patch:8.1.0945: internal error when using pattern with NL in the range
  * build: checkprefix: skip if empty #9624
  * vim-patch:8.1.0932: remove Farsi support (#9622)
  * terminal: Fix potential invalid local 'scrollback' (#9605)
  * API: nvim_create_buf: add `scratch` parameter
  * build/Makefile: validate prefix for specific targets (#9621)
  * vim-patch:8.1.0803: session restore: handle single quotes #9620
  * build/Makefile: check CMAKE_INSTALL_PREFIX
  * build/CMakeLists.txt: group related logic
  * clang/"null pointer dereference": win_rotate
  * PVS/V1028: cast operands, not the result
  * Add tests for terminal background detection
  * Automatically detect terminal background and set bg=dark or bg=light
* Sat Mar 16 2019 mcepl@cepl.eu
- Update to version 0.4.0~git.1552765270.5c836d2ef:
  * Allow using internal popupmenu or ext_popupmenu for wildmenu
  * oldtests: wait 200ms on mac for timer test
  * vim-patch:8.1.0019: error when defining a Lambda with index of a function result
  * test: simplify TUI bg-detection test
  * vim-patch:8.1.0728: avoid breaking after single space #9733
  * autocmd: add MenuPopupChanged autocmd
  * vim-patch:8.1.0671: cursor in wrong column after auto-format #9729
  * compositor: fix rendering issues with floats opened after popupmenu
  * autocmd: do not show empty section after ++once handlers expire
  * autocmd: rename: "++nested", "++once"
  * vim-patch:8.0.1447: still too many old style tests (#9725)
  * dictwatcheradd(): support b:changedtick #9693
  * TextYankPost: add v:event["inclusive"] #9717
  * vim-patch:8.1.0170: invalid memory use with complicated pattern #9724
  * test/CI: skip "throttles output" test on Travis macOS #9721
  * docs: adjust the generated nvim_open_win docs
  * docs: update generated API docs
  * docs: floating windows introduction
  * floats: add NormalFloat highlight and 'nonumber' default
  * window: simplify logic for entering new float
  * autocmd: rename "once" => "-once" #9713
  * Dist: make icon a proper square (#9716)
  * TUI/background detection: hook into VimEnter event
  * cleanup: rename menu_nable_recurse() #9707
  * autocmd: introduce "once" feature
  * vim-patch:8.1.1002: "gf" on URL with port number #9705
  * executable(): return false if user is not owner #9703
  * vim-patch:8.1.0994: fix relative cursor position #9676
  * floating-window: fix crash setting cmdheight #9685
  * vim-patch:8.0.1372: profile log may be truncated halfway a character
  * vim-patch:8.1.0826: too many #ifdefs
  * oldtests: set shellslash in Test_true_false_arg()
  * oldtests: set shellslash in Test_shellescape()
  * vim-patch:8.1.0739: text objects in not sufficiently tested
  * vim-patch:8.1.0998: getcurpos() unexpectedly changes "curswant"
  * lint: fix coding style
  * vim-patch:8.0.0646: the hlsearch test fails on fast systems
  * vim-patch:8.0.0645: no error for illegal back reference in NFA engine
  * vim-patch:8.0.0644: the timeout for 'hlsearch' is not tested
  * vim-patch:8.0.0643: when a pattern search is slow Vim becomes unusable
  * vim-patch:8.1.0935: old regexp engine may use invalid buffer #9692
  * tui_tk_ti_getstr: handle weird value #9688
  * Fix os.getenv of lua on Windows
  * Fix environment variable on Windows
  * PVS/V560: window.c: fix always true condition #9682
  * buffer: use aucmd_prepbuf() instead of switch_to_win_for_buf()
  * vim-patch:8.1.0875: not all errors of marks and findfile()/finddir() are tested
  * vim-patch:8.1.0891: substitute command inssuficiently tested
  * PVS/V501: ui_compositor.c: identical sub-expressions #9673
  * edit.c: Disable indent during completion
  * api: add nvim_win_close() to close window by id
  * test: multibyte env var names #9655
  * os/env: Fix completion of multibyte env var names
  * vim-patch:8.1.0971: failure to select quoted text obj moves cursor #9658
  * floats: implement floating windows
  * ops.c: do_join expects `count` of 2 or greater #6855
  * vim-patch.sh: mention URL for `hub` tool #9659
  * search.c: remove dead code #5307
  * cleanup: remove legacy `enc_dbcs` global #9660
  * screen.c: remove dead code #6609
* Fri Mar  1 2019 opensuse-packaging@opensuse.org
- Update to version 0.4.0~git.1551466910.018e0d5a1:
  * API/buffer-updates: always detach on buf-reload #9643
  * os: remove uv_translate_sys_error impl #9652
  * vim-patch:8.1.0973: pattern with syntax error gives threee error messages
  * vim-patch:8.1.0965: search test fails
  * vim-patch:8.1.0963: illegal memory access when using 'incsearch'
  * vim-patch:8.1.0968: crash when using search pattern \%%Ufffffc23
  * test: fix isCI() for Quickbuild
  * test/env: multibyte env var to child process
  * clint: check env functions
  * vim-patch:8.1.0985: crash with large number in regexp
  * os/env: use libuv v1.12 getenv/setenv API
  * os_getenv, os_setenv: revert "widechar" impl
  * win: os_getenv(): use _wgetenv()
  * utf16_to_utf8: minor fixes
  * os_setenv: use _wputenv_s; remove vestigial code #7920
* Thu Feb 28 2019 Matej Cepl <mcepl@suse.com>
- Rebuilt
* Tue Feb 26 2019 opensuse-packaging@opensuse.org
- Update to version 0.4.0~git.1551133812.533d4a36e:
  * TUI: do not resize host-terminal on startup (#9645)
* Mon Feb 25 2019 opensuse-packaging@opensuse.org
- Update to version 0.4.0~git.1551090895.88652c49a:
  * vim-patch:8.1.0980: extend() insufficiently tested (#9646)
  * vim-patch:8.1.0225: mode() does not indicate using CTRL-O from Insert mode (#9644)
  * vim-patch:8.1.0959: sorting large numbers is not tested (#9641)
  * TUI: rework background-color detection
  * win/deps: update to (forked) libuv v1.26.0
  * I/O: ignore ENOTSUP for failed fsync()
  * deps: update to libuv v1.26.0
  * fix "E667: Fsync failed" on macOS
  * man.vim: g:man_hardwrap #9633
  * vim-patch:8.1.0276: no test for 'incsearch' highlighting with :s
  * vim-patch:8.1.0387: no test for 'ambiwidth' detection
  * vim-patch:8.1.0668: no test for overstrike mode in the command line
  * vim-patch:8.1.0937: invalid memory access in search pattern
  * vim-patch:8.1.0934: invalid memory access in search pattern
  * vim-patch:8.1.0926: no test for :wnext, :wNext and :wprevious
  * lint
  * vim-patch:8.1.0945: internal error when using pattern with NL in the range
  * build: checkprefix: skip if empty #9624
  * vim-patch:8.1.0932: remove Farsi support (#9622)
  * terminal: Fix potential invalid local 'scrollback' (#9605)
  * API: nvim_create_buf: add `scratch` parameter
  * build/Makefile: validate prefix for specific targets (#9621)
  * vim-patch:8.1.0803: session restore: handle single quotes #9620
  * build/Makefile: check CMAKE_INSTALL_PREFIX
  * build/CMakeLists.txt: group related logic
  * clang/"null pointer dereference": win_rotate
  * PVS/V1028: cast operands, not the result
  * Add tests for terminal background detection
  * Automatically detect terminal background and set bg=dark or bg=light
* Wed Feb 13 2019 opensuse-packaging@opensuse.org
- Update to version 0.4.0~git.1550043030.969cc5599:
  * vim-patch:8.1.0852: findfile() and finddir() are not properly tested (#9609)
  * UI: change implementation of hl_rgb2cterm_color()
  * UI: 'pumblend' for cterm (256-color TUI)
* Tue Feb 12 2019 opensuse-packaging@opensuse.org
- Update to version 0.4.0~git.1549957870.9b4383261:
  * TUI: assume italics support in all xterm-likes
  * highlight: handle blending with gui=reverse and guisp attributes
  * TUI: sniff nsterm (Terminal.app) from $TERM_PROGRAM
  * TUI: force italics in tmux
  * TUI: italics in Terminal.app (nsterm)
  * ui: implement ext_messages
  * doc: 'fillchars' is local to window
  * api: add nvim_create_buf to create a new empty buffer.
* Fri Feb  8 2019 opensuse-packaging@opensuse.org
- Update to version 0.4.0~git.1549572105.f6faeea41:
  * screen: cleanup allocation, clearing and validation
  * screen: simplify scrolling code
  * UI: implement 'pumblend' option for semi-transparent popupmenu
  * man.vim: set 'linebreak'
* Wed Feb  6 2019 opensuse-packaging@opensuse.org
- Update to version 0.4.0~git.1549396747.c9b7f0c24:
  * UI: always use contrete colors for default_colors_set
  * build: PRAGMA_DIAG_PUSH_IGNORE_MISSING_PROTOTYPES
  * build: -Wmissing-prototypes
  * build: set compiler options in one place
  * options: set 'scrollback' to -1 by default #9563
  * events: add "Signal" event #9564
  * popupmenu: fix alignment of kind and extra after #9530
  * rename ui_is_external to ui_has (#9576)
  * vim-patch:8.0.1114: default for 'iminsert' is annoying
  * vim-patch:8.0.1077: no debugger making use of the terminal window
  * vim-patch:8.0.1073: may get an endless loop if 'statusline' changes a highlight
  * multigrid: reset win scrolling after swap message
  * tests/ui: add test for popupmenu redrawing in various situations
  * ui/compositor: add redraws needed due to intersected doublewidth chars.
  * vim-patch:8.1.0792: bad display if opening cmdline window from Insert completion
  * Reduce pum redraws from edit.c by delaying undisplay of pum
  * UI: add "compositor" layer to merge grids for TUI use in a correct way
  * vim-patch:8.0.1045: running tests may pollute shell history
  * inccommand: auto-disable if folding is slow #9568
* Thu Jan 31 2019 mcepl@suse.com
- Update to version 0.4.0~git.1548970032.ada82f348:
  * test: adjust timer_spec
  * test: improve reliability of ":terminal topline" test
- Define %%python3_pkgversion for compatibility with Fedora/RHEL7.
* Wed Jan 30 2019 opensuse-packaging@opensuse.org
- Update to version 0.4.0~git.1548727248.894f6bee5:
  * :terminal : set topline based on window height #8325
  * doc [ci skip] (#9553)
  * screen: simplify wp->w_lines allocation logic
  * terminal: handle size when switching buffers in window
  * window/ui: reorganize size variables, fix terminal window size with multigrid.
  * screen: remove superfluous default_grid indirection for global size
  * terminal: simplify sizing logic
  * vim-patch:8.0.0413: menu test fails on MS-Windows #8173
  * menu_get(): fix query behavior
  * menu_get(): Do not include empty items
  * fix ":menu Item.SubItem"
  * gen_api_vimdoc.py: Do not wrap on hyphens, long words
  * doc [ci skip] #9478
  * tests: 'fcs' and 'lcs' are local to the window
  * vim-patch:8.1.0759: showing two characters for tab is limited
  * linter: fix issues
  * tests: fix mouse tests that use lcs=eol:$
  * options: make 'fillchars'/'listchars' local to window
  * vim-patch:8.0.0412: menu test fails on MS-Windows
  * vim-patch:8.0.0411: menu translations don't match when case is changed.
  * checkhealth: validate locale (#9548)
* Fri Jan 25 2019 opensuse-packaging@opensuse.org
- Update to version 0.4.0~git.1548272924.6e6bc3b6c:
  * :terminal : Fix F1-F4 key codes (#9535)
  * tests/lua: test for multiline error messages in lua
  * cleanup: reduce some duplicate code, avoid function pointers for a condition
  * ex_echo: reuse code from message.c to show arg to user
  * message.c: add msg_echo_attr functions, use it for lua error messages
  * Fix api doc nvim_buf_lines_event example
  * PVS/V1028 (rework): cast operands, not the result #9531
  * CI/codecov: fix invalid yaml [ci skip]
  * build: Fix -Wconversion warnings for fpclassify et al
  * build: Fix -Wconversion warnings for fpclassify et al
  * CI/codecov: remove "only_pulls" directive [ci skip]
* Sun Jan 20 2019 opensuse-packaging@opensuse.org
- Update to version 0.4.0~git.1548010718.7e3300f71:
  * ui: multigrid mouse support
  * STRICT_ADD, STRICT_SUB: Log error before abort
  * build: include auto/config.h explicitly
  * Remove support for using jemalloc instead of the system allocator
  * pvscheck.sh: set --sourcetree-root [ci skip]
  * pvscheck.sh: do not set --sourcetree-root [ci skip]
  * pvscheck.sh: ignore stddef.h
  * PVS/V560: expression is always true
  * clang/"null pointer dereference": expand_wildcards
  * PVS/V1032: pointer cast to a more strictly aligned type
  * PVS/V1032: pointer cast to a more strictly aligned type
  * PVS/V1028: cast operands, not the result
  * PVS/V501: diff.c: silence warning
  * test: Lua 5.2/5.3 compat
  * ci: switch to Xcode 10.1 / macOS 10.13
  * tests: load-adjust timer tests (functionaltest)
  * tests: load-adjust timer tests (oldtest)
  * tests: fix Test_help_tagjump()
* Thu Jan 17 2019 opensuse-packaging@opensuse.org
- Switch to more _services.
- Update neovim-lua-compatibility.patch when we have vim.compat
  library available.
* Thu Jan 17 2019 opensuse-packaging@opensuse.org
- Update to version 0.4.0~git.1547583542.279043d62:
  * screen: don't unconditionally clear messages on window scroll
- Also refresh 6856.patch against the current master.
* Tue Jan 15 2019 opensuse-packaging@opensuse.org
- Update to version 0.4.0~git.1547509673.95fa71c6d:
  * :recover : Fix crash on non-existent *.swp #9504
  * lua: expose full interface of vim.inspect and add test
  * lua/stdlib: Load runtime modules on-demand
  * lua/stdlib: vim.inspect, string functions
  * test/API: nvim_set_vvar() #9395
  * API: nvim_set_vvar(): set v: variables #9395
  * dict_set_var: check value before checking its container
  * pvscheck.sh: Fix download URL #9500
- Update patches neovim-0.1.7-bitop.patch and
  neovim-0.2.0-gcc-prototype.patch
* Fri Jan 11 2019 opensuse-packaging@opensuse.org
- Update to version 0.4.0~git.1547206217.8853fca1f:
  * screen: make update_screen() the only entry point for redrawing
  * version.c: update [ci skip] (#9444)
  * vim-patch:8.1.0450: build failure without the +fold feature
  * vim-patch:8.1.0449: fix display of 'rnu' with folded lines #9481
  * clipboard/macOS: assume that pbcopy works #9480
  * vim-patch:8.1.0648: custom operators can't act upon forced motion
  * CMake: Feature-detect __builtin_{add,sub}_overflow
  * PVS/V1028: cast operands, not the result
  * assert.h: Check overflow with STRICT_ADD, STRICT_SUB
  * bufhl: simplify redraw logic
  * remove dead argument of redrawWinline
  * screen: avoid redrawing windows immediately when debug signs are placed.
  * health/pythonx: handle "pip upgrade failure"
  * health/pythonx: refactor #Detect()
  * health/pythonx: refactor pyenv check
* Mon Jan  7 2019 Matej Cepl <mcepl@suse.com>
- Actually python-neovim is more prevalent than -nvim.
* Sat Jan  5 2019 opensuse-packaging@opensuse.org
- Update to version 0.4.0~git.1546641921.38b4ca26b:
  * PVS/V547: window.c: Expression is always true
  * PVS/V547: viml/parser/expressions.c: Expression is always true
  * PVS/V751: tui.c, Parameter is not used
  * PVS/V535: shada.c: variable reassigned in inner loop
  * PVS/V547: diff.c: xmalloc() never returns NULL
  * PVS/V547: diff.c: Expression is always true
  * PVS/V501: diff.c: silence warning
  * release.sh: Format issue-numbers in descriptions [ci skip]
  * release.sh: fix exclusion pattern [ci skip]
  * build: remove cmake/GenerateHelptags.cmake.in
  * build: fix `doc_html` target
  * Visual: highlight char-at-cursor
  * remove check_visual_highlight()
  * vim-patch:8.1.0653: arglist test fails on MS-windows
  * vim-patch:8.1.0651: :args \"foo works like :args without argument
  * TUI: Do not disable BCE for builtin terminfos (#9443)
  * UGRID_FOREACH_CELL: avoid shadowed variables
  * build: enable -Wshadow
  * vim-patch:8.0.0251: not easy to select Python 2 or 3 (#9173)
  * health/provider: Check for available pynvim when neovim module missing
  * python#CheckForModule: Use the given module string instead of hard-coding pynvim
  * {health,provider}/python: Import the neovim, rather than pynvim, module
* Wed Jan  2 2019 opensuse-packaging@opensuse.org
- Update to version 0.4.0~git.1546377717.5a11e5535:
  * Mark "shell command :! throttles shell-command output greater than ~10KB" fragile
  * Mark "feeding large chunks of input with <Paste>" fragile
  * Mark ":substitute with inccommand during :terminal activity" fragile
  * popupmenu: fix positioning with vsplits
  * travis: Only run lint job for master branch/PRs
  * multigrid: do all adjustment in screen.c
  * travis: Run ci for release-* branches
* Sun Dec 30 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1546182312.fa5182489:
  * vim-patch:8.1.0662: needlessly searching for tilde in string
  * vim-patch:8.1.0354: packadd test fails on MS-Windows
  * vim-patch:8.1.0353: an "after" directory of a package is appended to 'rtp'
  * vim-patch:8.0.1734: package directory not added to 'rtp' if prefix matches
  * vim-patch:8.0.1469: when package path is a symlink 'runtimepath' is wrong
  * TUI: enter/exit alternate screen with "title stacking" (#9407)
  * rplugin.vim: Add migration support for Windows, nvim/ -> nvim-data/
  * ci: install neovim gem on macOS
  * ci: use homebrew addon to simplify shell scripts
  * Use stdpath() to determine rplugin manifest path
* Thu Dec 20 2018 Matej Cepl <mcepl@suse.com>
- Add to the system-wide configuration file extension of runtimepath by
  /usr/share/vim/site, so that neovim uses other Vim plugins installed
  from packages.
- Add /usr/share/vim/site tree of directories to be owned by neovim as
  well.
* Wed Dec 19 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1545198162.ccb005b9e:
  * genappimage: Unset $ARGV0 at invocation #9376
  * l10n: Update Ukrainian translation #9377
  * strings: use (u)int16_t for %%h printf format
  * vim-patch:8.1.0596: not all parts of printf() are tested
  * startup: Use $XDG_CONFIG_DIRS/nvim/sysinit.vim if it exists
  * CI/AppVeyor: install "pynvim" python package #9371
  * TUI: TERM=nsterm
  * TUI: detect BSD vt console
  * TUI: handle wrap of doublewidth chars correctly
  * vim-patch:8.1.0588: cannot define a sign with space in the text
  * vim-patch:8.1.0585: undo test may fail on MS-Windows
  * TUI: Konsole 18.07.70 supports DECSCUSR (#9364)
  * os/lang: use the correct LC_NUMERIC also for OS X
  * ex_docmd: '/' is not a path for Cmdline* events
  * vim-patch:8.0.1748: CmdlineEnter command uses backslash instead of slash
  * test: :ruby reports E319 if provider is missing
  * provider: make :ruby provider check use same code path as :python
  * cmdline: support v:event in CmdlineChanged
  * vim-patch:8.0.1445: cannot act on edits in the command line
  * provider: repurpose E319
  * ex_cmds: Remove various "not implemented" commands
  * provider: improve error message (#9344)
  * TUI: alacritty supports set_cursor_color #9353
  * macOS: infer primary language if $LANG is empty #9345
  * TUI: don't use BCE with attributes affecting background
* Mon Dec 10 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1544407916.55c518588:
  * vim-patch:8.1.0574: 'commentstring', fold marker in C (#9339)
  * vim-patch:8.1.0562: parsing of 'diffopt' is slightly wrong
  * vim-patch:8.1.0513: no error for set diffopt+=algorithm:
  * vim-patch:8.1.0502: internal diff fails when diffing a context diff
  * vim-patch:8.1.0497: :%%diffput changes order of lines
  * vim-patch:8.1.0458: ml_get error and crash when using "do"
  * vim-patch:8.1.0402: the DiffUpdate event isn't triggered for :diffput
  * vim-patch:8.1.0400: using freed memory with :diffget
  * vim-patch:8.1.0397: no event triggered after updating diffs
  * vim-patch:8.1.0395: compiler warning on 64-bit MS-Windows
  * vim-patch:8.1.0394: diffs are not always updated correctly
  * vim-patch:8.1.0393: not all white space difference options available
  * vim-patch:8.1.0375: cannot use diff mode with Cygwin diff.exe
  * vim-patch:8.1.0360: using an external diff program is slow and inflexible
  * Calm down the clinter
  * doc (#9288)
  * vim-patch:8.1.0570: 'commentstring' not used when adding fold marker (#9331)
  * runtime/syntax: Fix highlighting of augroup contents (#9328)
  * CI/Travis: install gperf using package manager (#9325)
  * api: make nvim_buf_set_virtual_text use correct namespace counter
  * vim-patch:8.1.0564: setting v:errors to wrong type still possible
  * vim-patch:8.1.0563: setting v:errors to a string give confusing error
* Fri Dec  7 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1544055259.769762834:
  * vim-patch:8.0.1425: execute() does not work in completion of user command (#9317)
  * screen: add missing status redraw when redraw_later(CLEAR) was used
  * provider/lang: expand() g:foo_host_prog (#9312)
  * clipboard: Revert unused check #9309
  * vim-patch:8.1.0559: command line completion not sufficiently tested
  * RPC: turn errors from async calls into notifications
  * codecov: Tolerate a 1%% drop in coverage for a PR
* Mon Dec  3 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1543792028.07ad5d71a:
  * clipboard: Support custom VimL functions #9304
  * cmake: Update comment on why CMP0059 is still set to OLD
  * Unset CMAKE_REQUIRED_* after they're done being used
  * clipboard: Prefer xclip (#9302)
  * doc: deprecate inputdialog()
  * VimL/confirm(): Show dialog even if :silent
  * insert: make <cmd> mapping work in completion (CTRL-X) mode
  * fixup: 30 col resize to scroll debug
  * fixup: 35 col resize to scroll screen
  * functionaltests: vim-patch:8.1.{550,551} fix
  * vim-patch:8.1.0551: expression evaluation may repeat an error message
  * vim-patch:8.1.0550: expression evaluation may repeat an error message
  * vim-patch:8.1.0553: it is not easy to edit a script that was sourced (#9298)
  * test/macOS: adjust time-sensitive tests
  * highlight: Fix missing .rgb_sp_color in initializers (#9287)
  * test: adjust time-sensitive tests
  * API: rename nvim_buf_clear_highlight to nvim_buf_clear_namespace
  * vim-patch:8.1.0098: segfault when pattern with \z() is very slow (#9283)
  * TUI: set_underline_color: only support colon form #9279
* Wed Nov 28 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1543373357.0d1e5ec1b:
  * scripts/gen_help_html.py
  * lint: src/.clang-format
  * matchit.vim: s:MultiMatch(): return Dict
  * doc
  * diff/highlight: Fix GUI highlight for low-priority CursorLine (#9281)
* Tue Nov 27 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1543291143.3348eea42:
  * fix wrong winnr in getwininfo
  * preserve_exit: Ignore SIGHUP
  * diff/highlight: Show underline for low-priority CursorLine
  * diff/highlight: do not overlay low-priority CursorLine
  * refactor: Rename get_term_attr_entry
* Mon Nov 26 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1543188561.271c5df41:
  * version.c: update [ci skip] (#9171)
  * API: Implement nvim_win_set_buf() #9100
* Mon Nov 26 2018 Matěj Cepl <mcepl@suse.com>
- Modify Patch2 neovim-0.1.7-bitop.patch (we may not need it
  lua-bit32 dependency)
* Sun Nov 25 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1543148930.bac9f36d4:
  * CI/travis: Remove vestigial sudo:true
  * Downgrade to clang-4.0 to avoid false-positive warnings from clang
  * Remove extraneous parens to silence -Wparentheses-equality
  * xenial: fix clang error messages
  * travis: switch from Ubuntu 14.04 to 16.04
  * api: implement object namespaces
* Thu Nov 22 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1542799480.108566e7b:
  * clipboard.vim: check for win32yank.exe #9263
  * vim-patch:8.1.0038: popup test causes Vim to exit
  * vim-patch:8.0.1731: characters deleted on completion
  * CI/Travis/macOS: Fix "brew reinstall" invocation (#9259)
  * health/python: warn if pynvim upgrade failed
  * defaults: background=dark #2894 (#9205)
  * health/python: slightly improve output
  * provider/python: refactoring
  * vim-patch:8.0.1171: popup test is still a bit flaky
  * vim-patch:8.0.1165: popup test is still flaky
  * vim-patch:8.0.1163: popup test is flaky
  * vim-patch:8.0.1249: no error when WaitFor() gets an invalid wrong expression
  * vim-patch:8.0.0737: crash when X11 selection is very big
  * vim-patch:8.0.1427: the :leftabove modifier doesn't work for :copen
  * vim-patch:8.1.0398: no test for -o and -O command line arguments (#9253)
  * TUI: support TERM=nsterm (#9244)
  * vim-patch:8.1.0536: file time test fails when using NFS (#9251)
  * lint
  * vim-patch:8.1.0376: compiler warning for uninitialized variable
  * vim-patch:8.1.0318: the getftype() test may fail for char devices
  * vim-patch:8.1.0299: misplaced comment
  * vim-patch:8.1.0298: window resize test sometimes fails on Mac
  * doc/python: 'neovim' module was renamed to 'pynvim'
  * health/python: 'neovim' module was renamed to 'pynvim'
  * vim-patch:8.1.0258: not enough testing for the CompleteDone event
  * unit/mbyte_spec: Run utf_char2bytes test in batches of 0xFFF characters
  * vim-patch:8.1.0146: when $LANG is set the compiler test may fail (#9238)
  * vim-patch:8.1.0108: no Danish translations (#9235)
  * vim-patch:8.1.0527: using 'shiftwidth' from wrong buffer for folding (#9234)
  * vim-patch:8.1.0352: browsing compressed tar files does not always work
  * vim-patch:8.1.0311: filtering entries in a quickfix list is not easy
  * vim-patch:8.1.0143: matchit and matchparen don't handle E363
  * vim-patch:8.1.0115: the matchparen plugin may throw an error
  * clipboard: support Wayland (#9230)
  * vim-patch: add matchit doc
  * vim-patch: rename path to check_colors.vim
  * vim-patch: move test_urls.vim out of runtime/
  * vim-patch:8.0.1352: dead URLs in the help go unnoticed
  * lint
  * vim-patch:8.1.0096: inconsistent use of the word autocommands
  * vim-patch:8.0.1620: reading spell file has no good EOF detection
  * oldtests: skip Test_spellinfo()
  * vim-patch:8.1.0340: no test for :spellinfo
* Mon Nov 12 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1541959994.9f3fb6611:
  * vim-patch:8.1.0516: :move command sets 'modified' #9224
  * TUI: attrs -> attr_id refactor
  * UI/TUI: improvements and cleanups for scrolling and clearing
  * test: adjust time-sensitive tests (#9220)
  * vim-patch:8.1.0337: :file fails in quickfix command (#9215)
  * channel: avoid buffering output when only terminal and no callbacks are active
  * ui_options: also send when starting or from OptionSet
  * jobstart(): Fix hang on non-executable cwd #9204
* Wed Nov  7 2018 mcepl@suse.com
- Reintroduce 6856.patch (GH can generate patch for whole pull
  request) … separate plugin (like
  https://github.com/bfredl/nvim-lspmirror just doesn't work)
* Wed Nov  7 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1541583085.c4c74c388:
  * jobstart(): Fix hang on non-executable cwd #9204
* Tue Nov  6 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1541509102.769d164c7:
  * vim-patch:8.1.0511: ml_get error when calling a function with a range (#9207)
  * vim-patch:8.1.0512: 'helplang' default is inconsistent for C and C.UTF-8
  * vim-patch:8.1.0510: filter test fails when $LANG is C.UTF-8
  * build: relax find_package() version spec
  * doc: API
  * doc: fix/remove broken tag references
  * build: `make helphtml`
  * doc: merge sponsor.txt into intro.txt
  * runtime: delete rrhelper.vim
  * doc
  * doc: manpage
  * test/win: window_split_tab_spec: fix retry()
* Mon Nov  5 2018 Matej Cepl <mcepl@suse.com>
- When we BuildRequire lua51-bit32, we should Require it as well.
* Mon Nov  5 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1541384736.10ef90364:
  * test/win: window_split_tab_spec: increase retry() time
  * CI/AppVeyor: Avoid "warning" which causes non-zero retcode
  * test/timer_spec: relax lower-bound
  * test/win: retry unreliable SIGWINCH test
  * build: dependencies: specify minimum versions
  * vim-patch:8.1.0508: suspend test fails when run by root (#9196)
  * vim-patch:8.1.0507: .raml files not properly detected (#9195)
  * TUI: Avoid reset_cursor_color in old VTE #9191
  * vim-patch:8.1.0504: when CTRL-C is mapped it triggers InsertLeave (#9192)
  * vim-patch:8.0.1766: expanding abbreviation doesn't work
  * vim-patch:8.0.1758: open_line() returns TRUE/FALSE for success/failure
* Thu Nov  1 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1541093972.d62174bb6:
  * rebase on the top of the current master
* Wed Oct 31 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1540968892.13a55ae0b:
  * rebase on the top of the current master
* Wed Oct 24 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1540391493.2f5c6ad10:
  * rebase on the top of the current master
* Wed Oct 17 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.2~git.1539772027.73ed48271:
  * Add line ending under certain circumstances
  * Rename neovim to nvim
  * Start working on cleaning up API surface
* Mon Oct 15 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.1+git.1539632011.bfbcd8db7:
  * Make lsp#completion#omni function more according to spec.
  * First stab at textDocument rename.
  * Moved to a much clearner impl of cbs
  * Work on making handling better
  * Make hover not fail on empty string
  * Make autocmds buffer-local and not repeat
  * WIP: Show example of 'auto-hover'
  * Fix recursive loop of autocmds
  * WIP: Broken while fixing autocmds
  * WIP: Autocmd cleanup and removing vimscript where possible
* Fri Oct 12 2018 mcepl@suse.com
- Update to the latest rebase of lsp branch on top of the current
  master.
* Fri Oct  5 2018 Matěj Cepl <mcepl@suse.com>
- Change version back to 0.3.1+git.1538725926.ea927c9da
* Sun Sep 30 2018 mcepl@suse.com
- Testing pull request https://github.com/neovim/neovim/pull/6856
    Built-in LSP Support
- Add neovim-lua-compatibility.patch to cover for the
  incompatibility between lua 5.1 and lua >= 5.2
- Switch from lua to luajit, where available.
* Sun Sep 30 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.1+git.1538332785.3bdc34d06:
  * TUI: terminfo_start: use unibi_from_term directly (#9072)
  * man.vim: set $MANWIDTH=999
  * undo: Fix infinite loop if undo_read_byte returns EOF #2880
  * editorconfig: Fix charset name #9070
  * dialog_changed: Remove mistaken assert #9069
  * vim-patch:8.1.0067: syntax highlighting not working when re-entering a buffer
  * vim-patch:8.1.0066: nasty autocommand causes using freed memory
  * vim-patch:8.1.0068: nasty autocommands can still cause using freed memory
  * lint
  * globals: arg_had_last is bool
  * vim-patch:8.0.1485: weird autocmd may cause arglist to be changed recursively
  * test: check_cores(): Fix tmp dir exclusion (#9061)
  * vim-patch:8.1.0416: sort doesn't report deleted lines (#9062)
* Thu Sep 27 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.1+git.1538045971.64a8a8fd2:
  * vim-patch:8.1.0435: cursorline highlight not removed in some situation (#9059)
  * man.vim: Start at the top #9023
  * lint
  * tui: eliminate scrolling region data structure
  * vim-patch:8.1.0120: buffer 'modified' set even when :sort has no changes
  * tui: eliminate grid->attrs, use indexed cell->attr
  * vim-patch:8.1.0436: can get the text of inputsecret() with getcmdline()
  * vim-patch:8.1.0433: mapping can obtain text from inputsecret()
  * terminal: Redraw statusline on title change #8973
  * TUI: Alacritty supports DECSCUSR (#9048)
  * log: Assert that we haven't started freeing memory before logging
  * os_unix: Log exit code before freeing all memory
  * deps: revert to jemalloc 4.5.0 (#9035)
  * build: Unify USE_BUNDLED, USE_BUNDLED_DEPS (#9046)
  * vim-patch:8.1.0428: the :suspend command is not tested (#9043)
  * vim-patch:8.1.0429: no test for :lcd with 'shellslash' (#9041)
  * minor: tui: update_attrs: code consistency
  * vim-patch:8.0.1557: printf() does not work with only one argument (#9038)
  * test: Do not load entire log-file into memory
  * swapfile: Always show swap dialog (E325)
  * shortmess+=F: Hide :bnext, :bprev fileinfo messages
  * vim-patch:8.1.0389: :behave command is not tested (#9030)
  * func_attr.h: FUNC_ATTR_PRINTF
  * vim-patch:8.0.0370: invalid memory access when setting wildchar empty
  * vim-patch:8.0.0368: not all options are tested with a range of values
  * vim-patch:8.1.0414: v:option_old is cleared when using :set in OptionSet autocmd
  * startup: always wait for UI with --embed, unless --headless also is supplied
  * TUI: Reset cursor color when applicable #8572
  * test/old: test_options: Accommodate Nvim default
  * vim-patch:8.1.0310: file info msg with 'F' in 'shortmess'
  * vim-patch:8.0.0682: no test for synIDtrans() (#8966)
  * man.vim: Fix very long justified lines #9023
  * man.vim: Ignore $MANWIDTH, use soft wrap #9023
  * shell/logging: Fix E730 with verbose system({List}) #9009
  * lint
  * replace fallthrough comment with macro
  * vim-patch:8.0.1215: newer gcc warns for implicit fallthrough
  * startup: don't erase screen on `:hi Normal` during startup
  * doc: test/README.md (#9020)
  * cleanup/TUI: remove old unused code #9013
  * log: RPC, input, other events
  * log: rename do_log to logmsg
  * test: system_spec: remove redundant clear()
  * startup: wait for embedder before executing startup commands and files
  * TUI: Skip redundant "stop" event (macOS kernel panic) (#9007)
  * vim-patch:8.0.1443: compiler complains about uninitialized variable
  * vim-patch:8.0.1428: compiler warning on 64 bit MS-Windows system
  * buffer: add support for virtual text annotations
  * lint
  * vim-patch:8.0.1417: test doesn't search for a sentence
  * vim-patch:8.0.1416: crash when searching for a sentence
  * oldtests: set nrformats to Vim default
  * runtime/colors: move check_colors.vim to runtime/tools
  * vim-patch:8.0.1400: color scheme check script shows up as color scheme
  * vim-patch:8.0.1395: it is not easy to see if a colorscheme is well written
  * vim-patch:8.0.1374: CTRL-A does not work with an empty line
  * loop_close: Drain thread_events (#8990)
  * vim-patch:8.1.0355 Incorrect adjusting the popup menu (#8996)
  * vim-patch:8.0.1363: recover swap file ending with .stz #9002
* Sat Sep 15 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.1+git.1536945669.dadcfe22c:
  * vim-patch:8.0.1201: "yL" is affected by 'scrolloff' (#8997)
  * lint
  * globals: KeyTyped is bool
  * vim-patch:8.0.1275: CmdlineLeave autocmd prevents fold from opening
  * vim-patch:8.1.0175: marks test fails in very wide window
  * vim-patch:8.1.0168: output of :marks is too short with multi-byte chars
  * vim-patch:8.0.1184: the :marks command is not tested
  * Update eval.c
  * getchar: allow <SID> in <Cmd> mapping
  * vim-patch:8.0.1089: range count in user command
  * vim-patch:8.0.1172: when E734 is given option is still set (#8988)
  * style: indent, then lint
  * vim-patch:8.1.0374: moving the cursor is slow when 'relativenumber' is set
  * vim-patch:8.1.0373: screen updating still slow when 'cursorline' is set
  * test: popupmenu placement
  * vim-patch:8.0.1161
  * popupmnu.c: Fix popup placement when preview window is below
  * vim-patch:8.1.0372: screen updating slow when 'cursorline' is set (#8986)
  * do_shell, do_filter: Remove "clear screen", "wait for return" calls
  * UI/cleanup: Remove most redraw_later_clear() calls
  * lint
  * vim-patch:8.0.1809: various typos
  * vim-patch:8.1.0219: expanding ## fails to escape backtick
  * vim-patch:8.1.0034: cursor not restored with ":edit #"
  * vim-patch:8.0.1154: 'indentkeys' does not work properly (#8980)
  * move: dir in onepage() is Direction
  * move: drop has_mbyte check
  * vim-patch:8.1.0174: after paging up and down fold line is wrong
  * vim-patch:8.1.0011: maparg() and mapcheck() confuse empty and non-existing (#8976)
  * vim-patch:8.0.1781: file names in quickfix window are not shortened
  * vim-patch:8.0.1378: autoload script sources itself when defining function
  * vim-patch:8.0.1377: cannot call a dict function in autoloaded dict
  * vim-patch:8.0.1115: crash when using foldtextresult() recursively (#8972)
  * CI/Codecov: disable changes status
  * ui: flush UI state on exit
  * lint: clean-up after parent commits
  * Remove has_mbytes local to lines changed in parent commit
  * Refactor: Remove occurences of mb_char2bytes
  * digraph: delete code that checks enc_utf8
  * digraph: refactor code that checks has_mbyte
  * tests: update expected output of :digraph command
  * vim-patch:8.0.0749: some unicode digraphs are hard to remember
  * oldtests: win: fix buffer pathsep
  * vim-patch:8.0.1040: cannot use another error format in getqflist()
  * lint
  * vim-patch:8.0.1031: "text" argument for getqflist() is confusing
  * vim-patch:8.0.1029: return value of getqflist() is inconsistent
  * test_largefile.vim: adjust comment to run it
  * vim-patch:8.0.1326: largefile test fails on CI, glob test on MS-Windows
  * vim-patch:8.0.0708: some tests are old style
  * vim-patch:8.0.1023: it is not easy to identify a quickfix list
  * vim-patch:8.0.1006: quickfix list changes when parsing text with 'erroformat'
  * ASAN/LeakSanitizer: fix typo in blacklist
  * vim-patch:8.0.0922: quickfix list always added after current one
  * vim-patch:8.0.0904: cannot set a location list from text
  * lint
  * main: advance in edit_buffers() is bool
  * window: refactor boolean variables in win_close()
  * cmake: add "generated-sources" target
  * vim-patch:8.0.0782: using freed memory in quickfix code
  * vim-patch:8.0.0733: can only add entries to one list in the quickfix stack
  * functests: Add tests
  * runtime/msgpack: Fix inf/nan regexp
  * test/win: job_spec: increase jobwait() timeout
  * test: API validation: assert exact string
  * API: Avoid overrun when formatting error-message
  * vim-patch:8.0.1595: no autocommand triggered before exiting
  * vim-patch:8.1.0334: 'autowrite' takes effect when buffer is not to be written
  * vim-patch:8.0.1190: unusable after opening new window in BufWritePre event
  * lint
  * ex_cmds: const variables in find_help_tags()
  * vim-patch:8.1.0235: more help tags that jump to the wrong location
  * vim-patch:8.0.1792: MS-Windows users expect -? to work like --help
  * vim-patch:8.1.0231: :help -? goes to help for -+
  * vim-patch:8.0.1383: local additions in help skips some files
  * vim-patch:8.0.0998: strange error when using K while only spaces are selected
  * CI/AppVeyor: Disable gcov build for PRs
  * tests: call getchar(1) in timer callback
  * lint
  * vim-patch:8.1.0052: when mapping to <Nop> times out the next mapping is skipped
  * vim-patch:8.0.1048: no test for what 8.0.1020 fixes
  * vim-patch:8.0.1020: when a timer calls getchar(1) input is overwritten
  * build/MSVC: remove libvterm-Fix-escape-sequences-for-MSVC.patch
  * deps: update libvterm
  * deps: update to jemalloc 5.1.0
  * tui: Hint wrapped lines to terminals.
  * Add tests for highlighting after the end of a line.
  * vim-patch:8.1.0344: 'hlsearch' highlighting has a gap after /$
  * screen.lua: extend snapshot_util() to work with extension state
  * oldtests: win: fix pathsep in :mkview test
  * vim-patch:8.1.0336: mkview test still fails on CI
  * vim-patch:8.1.0335: mkview test fails on CI
  * vim-patch:8.1.0333: :mkview does not restore cursor properly after "$"
  * vim-patch:8.1.0331: insufficient test coverage for :mkview and :loadview
  * doc/defaults: document `ttimeoutlen` default (#8943)
  * man.vim: guard against reload (#8940)
  * lint: clean-up after parent commits
  * Remove has_mbytes from lines local to parent commit
  * Refactor: remove mb_ptr2len_len, mb_ptr2cells and mb_ptr2cells_len
  * shell.c: fix scan-build NPE warning #8932
  * Fix dead assignment.
  * getchar: fix {read,copy,start}_redo() params
  * globals: cmd_silent is bool
  * vim-patch:8.1.0022: repeating put from expression register fails
  * test: Dump $NVIM_LOG_FILE contents (#8926)
  * lint
  * ex_cmds2: checkall in dialog_changed() is bool
  * vim-patch:8.1.0214 fixup: remove feature-guard
  * vim-patch:8.1.0214 (#8927)
  * vim-patch:8.0.0983: unnecessary check for NULL pointer
  * options: do not use gettext for +printheader (#8928)
  * API: nvim_unsubscribe(): Handle unknown events #8745
  * vim-patch:8.0.1001: setting 'encoding' makes 'printheader' invalid (#8925)
  * tests: introduce screen:expect{...} form
  * ext_cmdline: use new highlight representation for cmdline_block
  * health.vim: Detect missing init.vim
  * vim-patch:8.1.0322: Test_copy_winopt() does not restore 'hidden' (#8918)
  * oldtests: comment out test for 'set cpo+=.'
  * vim-patch:8.1.0144: the :cd command does not have good test coverage
  * win/dist: nvim-qt v0.2.10 (#8901)
  * vim-patch:8.1.0327: the "g CTRL-G" command isn't tested much (#8914)
  * src/nvim/testdir/Makefile: define NEW_TESTS automatically (#8909)
  * CI/Codecov: enable changes status (#8910)
  * vim-patch:8.0.1214: accessing freed memory when EXITFREE is set
  * runtime/doc: fix broken links found by `make html`
  * warn about tests without libintl
  * build/doc: generate vimindex.html
  * vim-patch:8.0.1468: illegal memory access in del_bytes()
  * vim-patch:8.0.0900: :tab options doesn't open a new tab page
  * vim-patch:8.0.1404: invalid memory access on exit
  * vim-patch:8.0.1228: invalid memory access in GUI test
  * vim-patch:8.0.0883: invalid memory access with nonsensical script
  * lint: cleanup after parent commits
  * Remove has_mbyte from lines near changes in parent commit
  * Remove occurences of mb_head_off
* Sat Aug 25 2018 mcepl@suse.com
- Put the system-wide config in /etc, and just a symlink to $VIM
* Sat Aug 25 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.1+git.1535098679.c0157e8fe:
  * remote/host.vim: specify {nosuf} for globpath() (#8882)
  * search: fix types of findsent() variables
  * vim-patch:8.1.0083: "is" and "as" have trouble with quoted punctuation
  * doc: remove mention of "drop" register (#8893)
  * oldtests: reindent Makefile to 8-width tab
  * editorconfig: Makefile uses 8-width tab indent
  * vim-patch:8.0.1682: auto indenting breaks inserting a block (#8892)
  * lint
  * vim-patch:8.0.1044: warning for uninitialized variable
  * vim-patch:8.0.1043: warning for uninitialized variable
  * vim-patch:8.0.1041: bogus characters when indenting during visual-block append
  * vim-patch:8.0.0999: indenting raw C++ strings is wrong
  * vim-patch:8.0.1151: "vim -c startinsert!" doesn't append (#8886)
  * vim-patch:8.0.1242: function argument with only dash is seen as number zero
  * vim-patch:8.0.1790: 'winfixwidth' is not always respected by :close
  * vim-patch:8.0.1707: when 'wfh' is set ":bel 10new" scrolls window
  * vim-patch:8.0.1426: "gf" and <cfile> don't accept ? and & in URL
  * vim-patch:8.0.1331: possible crash when window can be zero lines high
  * vim-patch:8.1.0303: line2byte() is wrong for last line with 'noeol'
  * vim-patch:8.1.0110: file name not displayed with ":file" (#8878)
  * vim-patch.sh: Also check for .git/ directory
  * lint
  * undo: undo_undoes is bool
  * undo: did_undo,absolute in u_undo_end() are bool
  * undo: update undo_time() function signature
  * undo: above,did_undo in undo_time() are bool
  * vim-patch:8.0.1441: using ":undo 0" leaves undo in wrong state
  * vim-patch.sh: Use git-rev-parse to check repo (#8875)
  * search: "include" in current_tagblock() is bool
  * vim-patch:8.1.0290: "cit" on an empty HTML tag changes the whole tag
  * lint
  * vim-patch:8.0.1487: test 14 fails
  * vim-patch:8.0.1486: accessing invalid memory with "it"
  * vim-patch:8.0.1291: C indent wrong when * immediately follows comment
  * vim-patch:8.1.0018: using "gn" may select wrong text when wrapping
  * vim-patch:8.0.1148: gN doesn't work on last match with 'wrapscan' off
  * vim-patch:8.0.0762: ml_get error with :psearch in buffer without a name
  * vim-patch:8.0.1418: no test for expanding backticks
  * doc: Remove irrelevant line about "only the first" vimrc is used
  * API: Remove path prefix from command name in nvim_get_proc()
  * lint
  * normal: don't check has_mbyte
  * vim-patch:8.0.1091: test for <cexpr> fails without +balloon_eval feature
  * vim-patch:8.0.1090: cannot get the text under the cursor like v:beval_text
  * vim-patch:8.1.0159: completion for user names does not work for a prefix.
  * ex_docmd: forceit,usefilter are bool
  * ops: refactor get_spec_reg()
  * vim-patch:8.0.1787: cannot insert the whole cursor line
  * vim-patch:8.1.0101: no test for getcmdwintype()
  * vim-patch:8.0.1816: no test for setcmdpos()
  * vim-patch:8.0.1649: no completion for argument list commands
  * vim-patch:8.0.1231: expanding file name drops dash
  * vim-patch:8.0.0878: no completion for :mapclear
  * vim-patch:8.0.1509: test for failing drag-n-drop command no longer fails
  * vim-patch:8.0.1508: the :drop command is not always available
  * vim-patch:8.1.0186: test for getwininfo() fails in GUI
  * vim-patch:8.1.0184: not easy to figure out the window layout
  * vim-patch:8.0.1364: there is no easy way to get the window position
  * API: Use `ps -o comm` in nvim_get_proc()
* Sat Aug 18 2018 mcepl@suse.com
- Actually, the correct location of sysinit.vim is /usr/share/nvim.
* Sat Aug 18 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.1+git.1534505627.c7db42faa:
  * cmdline: always use save_cmdline before command_line_enter
* Sat Aug 18 2018 opensuse-packaging@opensuse.org
- Correct name for the system-wide initialization is sysinit.vim,
  not just init.vim (boo#1098800)
* Thu Aug 16 2018 mcepl@suse.com
- Use %%cmake macro
* Thu Aug 16 2018 opensuse-packaging@opensuse.org
- Installation of the systemwide configuration file (boo#1098800)
- Update to version 0.3.1+git.1534330940.b5cfac089:
  * lint
  * vim-patch:8.0.1633: a TextChanged autocmd triggers when it is defined
  * vim-patch:8.0.1413: accessing freed memory in :cbuffer
  * oldtests: finish port of 8.0.1224
  * vim-patch:8.0.1409: buffer overflow in :tags command
  * vim-patch:8.0.1488: emacs tags no longer work
  * vim-patch:8.0.1218: writing to freed memory in autocmd
  * vim-patch:8.0.1209: still too many old style tests
  * TUI: use BCE again more often, as it provides smoother resizes and scrolling
  * tui: reenable cursor movement optimizations (leftover from #8221)
  * tui: hack for invalid first line with non-bce resize
  * tui: use bce properly
  * lint: clean up after parent commit
  * oldtests: win: a directory is not executable
  * vim-patch:8.1.0262: not enough testing for getftype()
  * vim-patch:8.0.1630: trimming white space is not that easy
  * vim-patch:8.1.0161: buffer not updated with 'autoread' set if file was deleted
  * Remove occurrences of 'has_mbyte' near lines changes by parent commit
  * Remove all occurrences of mb_off2cells
  * cursor_shape: use attribute ids instead of syntax ids
  * highlight: HlAttrs is a value type; treat it like such
  * lint
  * vim-patch:8.0.1397: pattern with \& following nothing gives an error
  * vim-patch:8.0.1257: no test for fix of undefined behavior
  * vim-patch:8.0.1243: no test for what 8.0.1227 fixes
  * vim-patch:8.0.1227: undefined left shift in readfile()
  * deps: get gperf-3.1.tar.gz from our mirror
  * CI/travis: fix restore from cache
  * eval: match in find_some_match() is bool
  * lint
  * regexp: drop has_mbyte check in regmatch()
  * vim-patch:8.0.1361: some users don't want to diff with hidden buffers
  * diff: drop enc_utf8 check in diff_equal_char()
  * vim-patch:8.0.1046: code duplication in diff mode
  * vim-patch:8.0.1037: "icase" of 'diffopt' is not used for highlighting
  * lint
  * vim-patch:8.1.0099: exclamation mark in error message not needed
  * vim-patch:8.1.0097: superfluous space before exclamation mark
  * vim-patch:8.1.0090: "..." used inconsistently in a message
  * vim-patch:8.1.0078: "..." used inconsistently in messages
  * vim-patch:8.0.1517: invalid memory acces with pattern using look-behind match
  * vim-patch:8.0.1470: integer overflow when using regexp pattern
  * vim-patch:8.0.1254: undefined left shift in gethexchrs()
  * vim-patch:8.0.0828: Coverity: may dereference NULL pointer
  * refactor: Replace vim_strrchr() with strrchar() (#8718)
  * terminfo: add header guard, stdint.h for int8_t (#8848)
  * tutor: don't set statusline (#8844)
  * lint
  * vim-patch:8.0.1490: number of spell regions is spread out through the code
  * terminfo: update built-in terminfo entries
  * terminfo: add scripts/update_terminfo.sh
  * vim-patch.sh: Fix replacement which converts #1234 to vim/vim#1234
  * oldtests: Test_undofile() passes
  * Fix lint
  * vim-patch:8.1.0256: using setline() in TextChangedI splits undo
  * vim-patch:8.1.0245: calling setline() in TextChangedI autocmd breaks undo
  * vim-patch:8.1.0057: popup menu displayed wrong when using autocmd
  * vim-patch:8.1.0025: no test for the undofile() function
  * vim-patch:8.0.1433: illegal memory access after undo
  * memline: fnamecmp_ino() returns bool
  * vim-patch:8.0.1819: swap file warning for file with non-existing directory
  * vim-patch:8.0.1290: seq_cur of undotree() wrong after undo
  * vim-patch:8.1.0024: test %% command (#8834)
  * vim-patch:8.1.0257: no test for pathshorten()
  * vim-patch:8.1.0204: inputlist() is not tested
  * vim-patch:8.1.0008: no test for strwidth()
  * vim-patch:8.0.1421: accessing invalid memory with overlong byte sequence
  * vim-patch:8.0.1410: hang when using count() with an empty string
  * vim-patch:8.0.1105: match() and matchend() are not tested
  * vim-patch:8.0.1004: matchstrpos() without a match returns too many items
  * vim-patch.sh: Pass directory name to find (#8830)
  * vim-patch:8.1.0241: effect of ":tabmove N" is not clear
  * vim-patch:8.1.0009: tabpages insufficiently tested
  * ruby: detect rbenv shims for other versions (#8733)
  * defaults: win: 'shellpipe' for cmd.exe (#8827)
  * oldtests: win: set shellpipe for cmd.exe
  * misc: fixpos in del_char() is bool
  * edit: end_insert in check_auto_format() is bool
  * edit: did_add_space is bool
  * memline: copy in ml_replace() is bool
  * ops: is_del in block_prep() is bool
  * window: no_display in restore_win() is bool
  * ops: add const to shift_block() variables
  * tests: win: fix pathsep of :compiler paths
  * vim-patch:8.1.0005: test for :compiler command fails on MS-Windows
  * vim-patch:8.1.0004: test for :compiler command sometimes fails
  * vim-patch:8.1.0003: the :compiler command is not tested
  * eval: add const to f_gettabvar() variables
  * edit: temp in ins_del() is const int
  * vim-patch:8.1.0007: no test for "o" and "O" in Visual block mode
  * vim-patch:8.0.1811: no test for winrestcmd()
  * vim-patch:8.0.1705: when making a vertical split the mode message isn't updated
  * vim-patch:8.0.1446: acessing freed memory after window command in auto command
  * vim-patch:8.0.1579: virtual replace test fails in GUI
  * vim-patch:8.0.1577: virtual replace test fails on MS-Windows
  * vim-patch:8.0.1575: crash when using virtual replace
  * vim-patch:8.0.0879: crash when shifting with huge number
  * vim-patch:8.0.1601: highlight test fails on Win32
  * vim-patch:8.0.1600: crash when setting t_Co to zero when 'termguicolors' is set
  * vim-patch:8.0.1169: highlignting one char too many with 'list' and 'cul'
  * vim-patch:8.0.1168: wrong highlighting with combination of match and 'cursorline'
  * vim-patch:8.0.1216: tabline is not always updated for :file command
  * vim-patch:8.0.1160: getting tab-local variable fails after closing window
  * vim-patch:8.0.0890: still many old style tests
  * style: fixing minor issues noted in code review.
  * Remove some occrrences of enc_utf8 and has_mbyte
  * lint: clean-up after parent commit
  * Remove all occurences of the mb_ptr2char macro
  * Fix crash in lang_init() on macOS if lang_region = NULL
  * vim-patch:8.0.0735: no indication that the quickfix window/buffer changed
  * vim-patch:8.0.0687: minor issues related to quickfix
* Mon Aug  6 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.1+git.1533575802.1593ee7cf:
  * lint
  * globals: did_ai is bool
  * globals: did_si is bool
  * globals: can_si is bool
  * globals: can_si_back is bool
  * edit: haveto_redraw (local variable) is bool
  * edit: can_cindent is bool
  * edit: fix variables in ins_mousescroll()
  * globals: typebuf_was_filled is bool
  * vim-patch:8.1.0240: g:actual_curbuf set in wrong scope (#8818)
  * vim-patch:8.0.1507: timer test is a bit flaky
  * vim-patch:8.0.0948: crash if timer closes window while dragging status line
  * vim-patch:8.0.0722: screen is messed by timer up at inputlist() prompt
  * vim-patch:8.0.0671: hang when typing CTRL-C in confirm() in timer
  * eval, ex_getln: Fix incompatible pointer types (#8792)
  * syntax.h: fix include #8742
  * misc: refactor plines_win{,_nofill}()
  * fold: add const to foldSplit() variables
  * fold: add const to foldUpdateIEMSRecurse() vars
  * fold: add const to foldUpdateIEMS() variables
  * fold: add const to checkSmall() variables
  * fold: declare and init vars in deleteFoldEntry()
  * fold: add const to foldMoveTo() variables
  * fold: add const to deleteFold() variables
  * fold: add const to hasFoldingWin() variables
  * ex_cmds: add const to helptags_one() variables
  * ex_cmds: add const to fix_help_buffer() variables
  * hardcopy: refactor mch_print_start_line()
  * hardcopy: bold,italic,underline are TriState
  * fold: use_level,maybe_small are bool
  * globals: virtual_op is TriState
  * fold: recursive in deleteFoldEntry() is bool
  * fold: fold_changed is bool
  * fold: finish in foldUpdateIEMSRecurse() is bool
  * screen: screen_cleared is TriState
  * fold: lineFolded() is bool
  * fold: check_closed() returns bool
  * search: refactor variables in findmatchlimit()
  * search: start_in_quotes in findmatchlimit is TriState
  * edit: dont_sync_undo is TriState
  * ex_cmds: refactor utf8 variables to TriState
  * menu: enable in ex_menu() is TriState
  * fold: fold_T.fd_small is TriState
  * diff: refactor diff_a_works to use TriState
  * clint: detect MAYBE and recommend TriState
  * syntax: syn_pattern.sp_syncing is bool
  * syntax: add const to get_syntax_attr() params
  * syntax: add const to syn_finish_line() params,vars
  * syntax: did_header is bool
  * syntax: disptick_T is uint16_t
  * syntax: scl_id is int
  * vim-patch:8.0.1088: occasional memory use after free
  * vim-patch:8.0.1078: using freed memory with ":hi Normal"
  * vim-patch:8.0.1072: :highlight command causes a redraw even when nothing changed
  * vim-patch:8.0.0831: with 8 colors the bold attribute is not set properly
  * vim-patch:8.0.0791: terminal colors depend on the system
  * syntax: refactor get_id_list()
  * syntax: refactor syn_combine_list()
  * syntax: syn_cluster_T.scl_list is int16_t*
  * syntax: refactor syn_current_attr()
  * syntax: use const on check_keyword_id() variables
  * syntax: syn_state.sst_next_list is int16_t*
  * syntax: current_next_list is int16_t*
  * syntax: update types of stateitem_T members
  * syntax: use const on syn_list_keywords() variables
  * syntax: update types for keyentry_T,sp_syn
  * syntax: use const on copy_id_list() params,vars
  * syntax: use const on add_keyword() params,vars
  * syntax: update types of syn_opt_arg_T members
  * syntax: use const on put_id_list() variables
  * vim-patch:8.0.1541: synpat_T is taking too much memory
  * system(): handle profiling and 'verbose' #8730
  * checkhealth: always report stderr with errors (#8783)
  * checkhealth: do not use exepath with host_prog (#8784)
  * log.c: Fix possible truncation in buffer (#8791)
  * lint
  * screen: add const and reindent update_debug_signs()
  * vim-patch:8.0.0837: signs can be drawn on top of console messages
  * screen.c: add update_window_hl to special redrawing entrypoints
  * tui: clip invalid regions on resize (#8779), fixes #8774
  * log.c: format: padding
  * DOC: regenerate api docs
  * DOC: add support for intro sections in api docs
  * functests: tests related to operations on unloaded buffers #7688
  * API: update docs WRT behaviours/methods for unloaded buffers #7688
  * API: add nvim_buf_is_loaded() #7688
  * API: buf_get_lines, buf_line_count handle unloaded buffers #7688
  * cmake: bump API version
  * vim-patch:8.0.1017: test for MS-Windows $HOME always passes
  * vim-patch:8.0.1012: MS-Windows: problem with $HOME when is was set internally
  * vim-patch:8.0.0810: MS-Windows: tests still hang
  * vim-patch:8.0.0806: tests may try to create XfakeHOME twice
  * vim-patch:8.0.0805: GUI test fails with gnome2
  * log.c: ISO 8601 date/time
  * log.c: include milliseconds
  * log.c: message format
  * rename: os_get_localtime => os_localtime
  * ui: fix glitches where scrolling region affects clearing of screen
  * screen.c: fix redrawing tabline when messages overflow screen
  * tests: add test for switching tabpage right after scroll
  * test: assert scroll region state for clear
  * tests: test for redrawing tabline when msgsep marker goes outside screen
  * file_search: free stackp if vim_findfile() failed
  * vim-patch:8.1.0111: .po files do not use recommended names
  * vim-patch:8.0.1839: script to check .po file doesn't check for plural header
  * vim-patch:8.0.1778: script to check translations does not always work
  * vim-patch:8.0.0835: translations check with msgfmt does not work
  * vim-patch:8.0.0830: translating messages is not ideal
  * vim-patch:8.0.0794: checking translations fails with multiple NL
  * vim-patch:8.0.0734: the script to check translations can be improved
  * vim-patch:8.0.0726: translations cleanup script is too conservative
  * vim-patch:8.0.1622: possible NULL pointer dereference
  * vim-patch:8.0.1512: warning for possibly using NULL pointer
  * vim-patch:8.0.1502: in out-of-memory situation character is not restored
  * build: Enable LTO (Link Time Optimization) #8654
  * doc: README: "Transitioning from Vim" note (#8763)
  * vim-patch:8.0.1765: CTRL-G j in Insert mode is incorrect when 'virtualedit' set (#8757)
  * vim-patch:8.0.1398: :packadd does not load packages from the "start" directory (#8762)
  * Make "v:errmsg", "v:shell_error" and "v:this_session" distinct
  * vim-patch:8.0.0493: crash with cd command with very long argument
  * man.vim: improve manSentence regex (#8764)
  * ui: add tests for hlstate extension
  * ui: docs for ext_newgrid and ext_hlstate
  * ui: use line-based rather than char-based updates in screen.c
  * ui: add TODO for non-working terminal linewrap
  * highlight: refactor to use stateful representation
  * highlight: extract low-level highlight logic from syntax, ui
  * version bump
  * hardcopy: refactor mch_print_text_out()
  * vim-patch:8.1.0056: crash when using :hardcopy with illegal byte
  * vim-patch:8.0.1503: access memory beyond end of string
  * startup: fix ":if 0|syntax on|endif" bug (#8731)
  * NVIM v0.3.1
  * gen_api_vimdoc.py: add whitespace before "~"
  * doc
  * vim-patch:8.0.1799: no test for :registers command
  * vim-patch:8.0.0727: message about what register to yank into is not translated
  * vim-patch:8.0.0724: the message for yanking doesn't indicate the register
* Wed Jul 18 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.0+git.1531751184.cd6e7e8cf:
  * dispatch.c: changed api_set_error_call
  * channel.c: Prevent channel_destroy_early() from freeing uninitialized rpc stuff
  * Check all child processes for exit in SIGCHLD handler
  * channel.c: refactor spaghetti code
  * Only waitpid() for processes that we care about
  * vim-patch:8.0.0630: it is not easy to work on lines without a match (#8734)
  * keymap: add commented events to match 8.0.0697
  * tests: <SNR> is represented as 'R' (ASCII)
  * terminal: handle &confirm and :confirm on unloading (#8726)
  * screen: truncate showmode messages
  * vim-patch:8.0.0{474,475,492,633,1251} (#8725)
  * man.vim: C highlighting for EXAMPLES section #8709
  * tests/screen.lua: treat "resize" like any other event
  * test/includes: Use ${gen_cdefs} when pre-processing headers
  * test: Rename includes/pre/uv-errno.h to includes/pre/uv.h
  * vim-patch:8.0.0697: recorded key sequences may become invalid
  * vim-patch.sh: Unwrap commit messages when reviewing PRs
  * vim-patch:8.0.0522: Win32: clipboard=unnamed in :global (#8717)
  * transstr_buf: fix length comparison #8681
  * test: build_stl_str_hl (#8703)
  * vim-patch:8.0.1464: add slash when completing directory #8684
  * Update unicode files
  * [WIP/RFC] Fix standout mode
  * vim-patch:8.0.1387: wordcount test is old style
  * vim-patch:8.0.1022: test 80 is old style
  * vim-patch:8.0.1253: still too many old style tests
  * vim-patch:8.0.1140: still old style tests
* Mon Jul  9 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.0+git.1531158921.44a284d71:
  * vim-patch.sh: review_commit: Fix regex for vim version
  * vim-patch.sh: Use single quotes to avoid doubling backslashes
  * man.vim: fix for mandoc (#8698)
  * TUI: urxvt: also send xterm focus-reporting seqs #8699
  * clint: use stdout for normal/expected output (#8700)
  * tests: endfunc allows uncommented bar
  * vim-patch: finish port of 8.0.0{654,663,667}
  * oldtests: fix func Test_echo_and_string()
  * vim-patch:8.0.0663: unexpected error with 'verbose' (#8692)
* Thu Jul  5 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.0+git.1530725036.2bfabd5bf:
  * provider/node: npm --loglevel silent (#8682)
  * vim-patch:8.0.0686: extra redraw when using CTRL-L in second window
  * vim-patch:8.0.0640: mismatch between help and actual message
* Tue Jul  3 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.0+git.1530567148.bd51a0cd0:
  * coverity/166184:  Null pointer dereference (FP)
  * test: nvim_buf_attach: reduce delay
  * test: nvim_buf_attach response after initial delay
  * test: buffer_updates: 10s timeout
  * coverity/108274: tty-test.c: Insecure data handling (#8666)
  * test: port kword_test to Lua for utf_char2bytes()
  * vim-patch:8.0.0252: not properly recognizing word characters between 128 and 255
  * API: emit nvim_buf_lines_event from :terminal #8616
  * vim-patch:8.0.0593: DRY: setting list/dict return value (#8639)
  * gen_api_vimdoc: Make executable and change #! to python3
  * ui: don't crash when 'writedelay' is set and redrawing inside an event handler
  * highlight: high-priority CursorLine if fg is set. #8578
  * doc (#8652)
  * oldtest: Disable tests that :py(3)do stop executing when buffer changes
  * vim-patch:8.0.0688: cannot resize the window in a FileType autocommand
  * vim-patch:8.0.0677: setting 'filetype' may switch buffers
* Tue Jun 26 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.0+git.1529996054.da6874a7b:
  * vim-patch:8.0.0707: freeing wrong memory with certain autocommands
  * vim-patch:8.0.0706: crash when cancelling the cmdline window in Ex mode
  * vim-patch:8.0.0704: problems with autocommands when opening help
  * Improved version of #8613
* Mon Jun 25 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.0+git.1529885695.1cbc83018:
  * API: nvim_win_set_cursor: set curswant #8613
  * vim-patch:8.1.0107: getting buffer option clears message (#8637)
  * test: update writefile test for invalid list items
  * l10n: Update Ukrainian translation (#8622)
  * vim-patch:8.0.0642: writefile() continues after detecting an error
  * vim-patch:8.0.0548: saving the redo buffer only works one time (#8629)
  * vim-patch:8.0.0535: leak when exiting user function (#8574)
  * vim-patch:8.0.0{538,539} (#8615)
  * win/deps: Fix copy to subdir (#8636)
  * vim-patch:8.0.0627: "gn" selects only one character with 'nowrapscan' (#8632)
  * checkhealth: Python: fix VIRTUAL_ENV check (#8628)
  * vim-patch:8.0.0544: cppcheck warnings (#8627)
* Fri Jun 22 2018 mcepl@suse.com
- Don't move configuration file, but install it correctly in the first
  place.
- Add SUSE-specific template for *.spec files
* Fri Jun 22 2018 mcepl@suse.com
- Move the systemwide initial configuration file to /etc/xdg/nvim
* Fri Jun 22 2018 opensuse-packaging@opensuse.org
- Update to version 0.3.0+git.1529657394.7f7802e64:
  * main: fix FALLTHROUGH hints (#8623)
  * defaults: shortmess+=F (#8619)
  * *: Replace b_changedtick with new always-inline functions
  * buffer: fix copying setl options for buffer currently displayed in another window
  * vim-patch:8.0.0648: possible use of NULL pointer
  * vim-patch:8.0.0621: :stag does not respect 'switchbuf'
  * vim-patch:8.0.0468: g< after aborting an Ex command (#7941)
  * vim-patch:8.0.{0632,1536} (#8609)
  * vim-patch:8.0.0616: not always setting 'background' correctly after :hi Normal (#8606)
  * vim-patch:8.0.0{469,581,583} (#8601)
  * vim-patch:8.0.0669: CTRL-N at start of the buffer does not work correctly (#8600)
  * vim-patch:8.0.0636: when reading the undo file fails may use uninitialized data (#8599)
  * vim-patch:8.0.0551: the typeahead buffer is reallocated too often (#8598)
  * vim-patch:8.0.0568: 1gd may hang
  * lint
  * vim-patch:8.0.0546: swap file exists briefly when opening the command window (#8588)
  * vim-patch:8.0.0549: no test for the 8g8 command
  * vim-patch:8.0.0617: hardcopy test hangs on MS-Windows
  * vim-patch:8.0.0615: using %% with :hardcopy wrongly escapes spaces
  * vim-patch:8.0.0537: illegal memory access with :z and large count (#8592)
  * vim-patch: Replace shell variables in printf with formatted args
  * vim-patch:8.0.0455: the mode test may hang (#8577)
  * vim-patch:8.0.0542: getpos() can return a negative line number (#8580)
  * vim-patch:8.0.0598: building with gcc 7.1 yields new warnings (#8585)
  * startup: delete empty stdin buffer if other files were opened
  * use wchar_t instead of WCHAR #6998
  * startup: go to buffer 2 if stdin is empty
  * vim-patch:8.0.0547: extra line break in verbosefile
  * vim-patch:8.0.0467: using g< after :for does not show the right output
  * cmake: Prefer add_definitions() for setting preprocessor defines
  * cmake: Comply with new CMP0054 policy
  * Raise minimum CMake version to 2.8.12 and remove compat code
  * cmake: Consolidate enabling of "undefined symbol" errors
  * cmake: Explicitly declare C as the project language
  * cmake: Check for GNU compiler, not Linux, to set -D_GNU_SOURCE
  * cmake: Organize targets into folders
  * startup: fix -E/-Es without `-u NONE`
  * Ex mode: use getexline() instead of getexmodeline()
  * syntax: refactor syn_finish_line to return bool
  * vim-patch:8.0.0481: unnecessary if statement
  * build/win: Add workaround for Windows command length limit
  * Revert "makedeps.bat"
  * deps: Build bundled dependencies automatically for IDEs
* Sun Jun 17 2018 mcepl@suse.com
- BuildRequires jemalloc-devel
* Sun Jun 17 2018 opensuse-packaging@opensuse.org
- Update to version 0.2.2+git.1529233555.3cc350696:
  * checkhealth: node.js: also search yarn #8528
  * vim-patch:8.0.0609: some people still don't know how to quit (#8571)
  * vim-patch:8.0.0625: shellescape() always escapes a newline (#8573)
  * vim-patch:8.0.0604: gF test fails still on MS-Windows
  * vim-patch:8.0.0603: gF test fails on MS-Windows
  * vim-patch:8.0.0602: when gF fails to edit the file the cursor still moves
  * fix lint
  * vim-patch:8.0.0545: edit test may fail on some systems
  * vim-patch:8.0.0543: test_edit causes older xfce4-terminal to close
  * vim-patch:8.0.0532: test with long directory name fails on Mac
  * vim-patch:8.0.0531: test with long directory name fails on non-unix systems
  * vim-patch:8.0.0530: buffer overflow when 'columns' is very big
  * vim-patch:8.0.0577: warning for uninitialized variable
  * vim-patch:8.0.0575: using freed memory when resetting 'indentexpr'
  * build/test: skip empty TEST_TAG, TEST_FILTER
  * gen_events.lua: define NUM_EVENTS as an enum value
  * get_maphash: fix off-by-one
  * fillchars: make checks more strict and improve tests
  * functionaltest: Use octal escapes for printf
  * Add ‘eob’ option to fillchars
  * lint
  * Fix implicit conversion warning (#8536)
  * options: remove 'maxcombine` option (always use 6)
  * screen: use UTF-8 representation
  * vim-patch:8.0.0596: crash when complete() called after complete_add()
  * test/ui: doublewidth rendering. multibyte and cmdwin chars in folded lines (#8534)
  * charset: include option_defs.h for breakat_flags
  * doc
  * vim-patch:8.0.0451: some macros are in lower case
  * version bump
  * NVIM v0.3.0
  * doc: API
  * doc/man: mention $NVIM_LOG_FILE
  * doc: job/channel, misc #7783
  * checkhealth: fix nodejs provider advice (#8522)
  * test: fix startup_spec
  * deps: bump lua client
  * vim-patch:8.0.0520: using a function pointer while the function is known (#8513)
  * vim-patch:8.0.0466: still macros that should be all-caps (#8510)
  * build/msvc: Add support for building gettext tools with MSVC
  * build/msvc: Add libiconv to bundled dependencies
  * refactor: buf_collect_lines (#8509)
  * vim-patch:8.0.0541: compiler warning on MS-Windows
  * vim-patch:8.0.0533: abbreviation doesn't work after backspacing newline
  * expand_env_esc: fix invalid memory access (#8508)
  * vim-patch:8.0.0525: completion for user command argument not tested (#8506)
  * vim-patch:8.0.0452: some macros are in lower case (#8505)
  * doc: API: api-buffer-updates
  * vim-patch:8.0.0355: using uninitialized memory when 'isfname' is empty (#8493)
  * vim-patch:8.0.0586: no test for mapping timing out (#8501)
  * vim-patch:8.0.0560: :windo allows for ! but it's not supported (#8500)
  * lint
  * terminal: flush vterm output buffer on pty output #8486
  * vim-patch:8.0.0523: dv} deletes part of a multi-byte character.
  * vim-patch:8.0.0256: missing changes to one file breaks test
  * API: validation: mention invalid method name (#8489)
  * vim-patch:8.0.0265: ml_get error when :pydo deletes lines (#8492)
  * vim-patch:8.0.0254: error message of assert functions (#8488)
  * vim-patch:8.0.0255: setpos() does not use the buffer argument for all marks
  * ex_getln.c: Fix PVS/V519: variable assigned twice
  * win/build: avoid "C4142: benign redefinition of type"
  * win: enable DYNAMIC_ICONV
  * makedeps.bat
  * win/build: download iconv, gettext tools
  * cmake/FindLibIntl.cmake: handle passive case explicitly
  * build/CMake: find_package(… REQUIRED)
  * vim-patch:8.0.0675: 'colorcolumn' has a higher priority than 'hlsearch' (#8483)
  * fixup: exclude node_modules/ for crash detection
  * vim-patch:8.0.0851: 'smartindent' is used even when 'indentexpr' is set (#8481)
  * test: give more time for nodejs
  * lint
  * vim-patch:8.0.0623: error for invalid regexp is not very informative
  * vim-patch:8.0.0529: line in test commented out
  * cleanup, test interactive -E
  * win/startup: remove --literal
  * startup: allow explicit "-" file arg with --headless
  * startup: fix -es/-Es so they are actually silent
  * startup: silent-mode is not `full_screen`
  * lint
  * startup: stdin-text with -E, -Es (improved Ex-mode)
  * startup: stdin-text with file args
  * startup: stdin as text instead of commands
  * main.c: remove check_tty(), delayed warning
  * lint
  * doc/man: brevity, clarity
  * vim-patches: 8.0.0399 8.0.0401 (#8475)
  * vim-patch:8.0.1237: ":set scroll&" often gives an error (#8473)
  * version.c: update [ci skip] (#8413)
  * deps: Fix libvterm and libtermkey escape sequences for MSVC
  * deps: Ignore whitespace when applying libuv patch
  * deps: Upgrade LuaRocks and remove patch
  * build/MSVC: TUI: Fix uninitialized variable
  * TUI: skip SIGWINCH during teardown #8470
  * oldtests: comment out highlight group assertions
  * oldtests: comment out v:none assertions
  * vim-patch:8.0.1311: no test for strpart()
  * vim-patch:8.0.0435: some functions are not tested
  * vim-patch:8.0.0261: not enough test coverage for eval functions
  * tui: handle termguicolors rgb value in bridge for now
  * vim-patch:8.0.0562: not enough test coverage for syntax commands
  * oldtests: add conceal check for patch 8.0.0562
  * ex_getln: remove msg_scrolled cargo-cult magic, fixes #8251
  * ex_getln: don't redraw statusline on top of scrolled messages
  * vim-patch:8.0.0558: :ownsyntax is not tested
  * wildmenu: close before redrawing statusline (#8453)
  * vim-patch:8.0.0519: character classes not well tested (#8460)
  * nvim_list_uis: include channel id
  * vim-patch:8.0.0516 (#8458)
  * vim-patch:8.0.1232: MS-Windows users are confused about default mappings
  * vim-patch:8.0.0321: errors when trying to use scripts in tiny version
  * vim-patch:8.0.0515: ml_get errors in silent Ex mode (#8452)
  * vim-patch:8.0.0511: message for skipping client-server tests is unclear
  * vim-patch:8.0.0507: client-server tests fail when $DISPLAY is not set
  * API: Accept empty lists as dictionaries
  * Add empty options dict to buf_attach
  * Rename some more, fixe borked renaming
  * Send changedtick as first event if buffer contents weren't requested
  * Unify updates_start and updates to lines_event
  * Use autogenerated declarations
  * Lint
  * Update test
  * Some renamings and doc changes
  * Try fixing that test on travis
  * Increase sendkeys timeout
  * Enable -Wconversion
  * The grand renaming
  * Doc
  * Fix memory leak
  * Fix tests on windows
  * Bump up buffer capacity to 2GB
  * Make LiveUpdate return lastline instead of numreplaced
  * Lint
  * Make separate functions to start/stop live updates
  * Adjust FUNC_API_SINCE for nvim_buf_live_updates
  * Add argument to not send a buffers content when updates are enabled
  * Update to latest master
  * Tests for buffer updates
  * API: Document buffer updates
  * API: Implement buffer updates
* Mon May 28 2018 opensuse-packaging@opensuse.org
- Update to version 0.2.2+git.1527442697.f711b6351:
  * Change to use bundled libuv to build luv
  * vim-patch:8.0.0505: failed window split for :stag not handled (#8439)
  * vim-patch:8.0.0496: insufficient testing for folding (#8438)
  * fixup: always delete Xfile, fix exit code check
  * win: test: close shada file before os.remove
  * win: test: delete sautest/
  * win: test: don't test symlink if not admin user
  * win: test: disable non-admin failing tests
  * vim-patch:8.0.0454: compiler warnings for "always true" comparison (#8431)
  * vim-patch:8.0.0503: endless loop in updating folds with 32 bit ints (#8433)
  * Change to use RUNTIME target for DLL installation
  * Change to not use library prefix on MSVC
  * Change conditions to more generally
  * Remove unnecessary copy of header
  * Change to always use cmake to build libuv on Windows
  * Change to use cmake to build libuv
  * Change to enable build by Ninja on Windows
* Wed May 23 2018 opensuse-packaging@opensuse.org
- Update to version 0.2.2+git.1527100467.418abfc9d:
  * api: list information about all channels/jobs.
  * doc: remove mentions of vimrc_example
  * test/old: fix test filename
  * win/build: Fix install (#8420)
  * deps: update to msgpack 3.0.0
  * socket.c: Ignore PVS/V547: False positive
  * getchar.c: Fix PVS/V522: Dereference of null pointer mp_match
  * strings.c: Fix PVS/V781: value of 'l + 1' is checked after it was used
  * win/package: move gui shim to its runtime folder (#8418)
  * vim-patch:8.0.0500: quotestar test is still a bit flaky
  * vim-patch:8.0.0495: quotestar test uses timer instead of timeout
  * vim-patch:8.0.0491: quotestar test fails when features are missing
  * vim-patch:8.0.0489: clipboard and "* register is not tested
  * version.c: update [ci skip] (#8118)
  * vim-patch:8.0.0559: setting ttytype to xxx does not always fail
  * vim-patch:8.0.0342: double free with EXITFREE and setting 'ttytype'
  * vim-patch:8.0.0304: assign test fails in the GUI
  * test/old: remove `abort` from test declaration
  * vim-patch:8.0.0497: arabic support is not fully tested (#8404)
  * win: set TERMINFO_DIRS at build-time (#8408)
  * terminal: tickle statusline on entering #8323
  * test: inccommand_spec: retry unreliable test (#8311)
  * cleanup
  * main.c: remove useless call
  * do not pass NULL to os_getenv
  * channel: avoid references to non-rooted vimL list with output
  * vim-patch:8.0.1494: no autocmd triggered in Insert mode with visible popup menu
- don't use %%make_build macro ... it is not supported on Leap 42.3
- we need more recent version of libuv1 for Leap 42.3
- add BR for filesystem package, so we don't have to own standard dirs.
* Wed May 23 2018 mcepl@suse.com
- Add dependency on lua51-bit32 for Leap 42.3
* Thu May 17 2018 mcepl@suse.com
- Remove superfluous macros from SPEC file
* Thu May 17 2018 opensuse-packaging@opensuse.org
- Update to version 0.2.2+git.1526541294.e121b1dbe:
  * mf_open(): never fails (except for OOM)
  * coverity/13702: open_spellbuf: handle failed ml_open()
  * coverity/13713: do_pending_operator: handle failed u_save_cursor()
  * coverity/13709: spell_add_word: handle failed fseek()
  * coverity/13700: ignore failed win_split()
  * coverity/13969: handle u_save() failure
  * clint
  * Update documentation
  * 'keymap' now uses :lmap instead of :lnoremap
  * Split :lnoremap test into done and pending
  * :lnoremap mappings should not be remapped when replaying a recording
  * Ensure :lmap mappings take preference
  * Record :lmap transformed keys in gotchars()
  * Account for :lmap in macros
  * Add some basic tests for macros
* Thu May 17 2018 mcepl@suse.com
- Leap has lua51-LPeg instead of lua51-lpeg
* Wed May 16 2018 mcepl@suse.com
- Add _service file
- Update to version 0.2.2+git20180515.de7a0bdc3:
  * test: nodejs_spec: fix test after upstream API change
  * timer: make sure to free callback after the last timer due callback
  * API: nvim_get_commands(): return Dictionary
  * API: nvim_get_commands(): builtin is irrelevant for buffer-local
  * API: nvim_get_commands(): more attributes
  * API: nvim_get_commands(): always return keys
  * API: nvim_get_commands()
  * lint
  * api: Make nvim_set_option() update `:verbose set ...`
* Mon Apr  2 2018 mcepl@cepl.eu
- The first build of neovim which hopefully follows OpenSUSE standards.
