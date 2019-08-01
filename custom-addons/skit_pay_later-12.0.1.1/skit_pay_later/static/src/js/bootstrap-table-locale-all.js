/**
 * Bootstrap Table Afrikaans translation
 * Author: Phillip Kruger <phillip.kruger@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['af-ZA'] = {
        formatLoadingMessage: function () {
            return 'Besig om te laai, wag asseblief ...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' rekords per bladsy';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Resultate ' + pageFrom + ' tot ' + pageTo + ' van ' + totalRows + ' rye';
        },
        formatSearch: function () {
            return 'Soek';
        },
        formatNoMatches: function () {
            return 'Geen rekords gevind nie';
        },
        formatPaginationSwitch: function () {
            return 'Wys/verberg bladsy nummering';
        },
        formatRefresh: function () {
            return 'Herlaai';
        },
        formatToggle: function () {
            return 'Wissel';
        },
        formatColumns: function () {
            return 'Kolomme';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['af-ZA']);

})(jQuery);

/**
 * Bootstrap Table English translation
 * Author: Zhixin Wen<wenzhixin2010@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['ar-SA'] = {
        formatLoadingMessage: function () {
            return 'Ø¬Ø§Ø±ÙŠ Ø§Ù„ØªØ­Ù…ÙŠÙ„, ÙŠØ±Ø¬Ù‰ Ø§Ù„Ø¥Ù†ØªØ¸Ø§Ø±...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' Ø³Ø¬Ù„ Ù„ÙƒÙ„ ØµÙ�Ø­Ø©';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Ø§Ù„Ø¸Ø§Ù‡Ø± ' + pageFrom + ' Ø¥Ù„Ù‰ ' + pageTo + ' Ù…Ù† ' + totalRows + ' Ø³Ø¬Ù„';
        },
        formatSearch: function () {
            return 'Ø¨Ø­Ø«';
        },
        formatNoMatches: function () {
            return 'Ù„Ø§ ØªÙˆØ¬Ø¯ Ù†ØªØ§Ø¦Ø¬ Ù…Ø·Ø§Ø¨Ù‚Ø© Ù„Ù„Ø¨Ø­Ø«';
        },
        formatPaginationSwitch: function () {
            return 'Ø¥Ø®Ù�Ø§Ø¡\Ø¥Ø¸Ù‡Ø§Ø± ØªØ±Ù‚ÙŠÙ… Ø§Ù„ØµÙ�Ø­Ø§Øª';
        },
        formatRefresh: function () {
            return 'ØªØ­Ø¯ÙŠØ«';
        },
        formatToggle: function () {
            return 'ØªØºÙŠÙŠØ±';
        },
        formatColumns: function () {
            return 'Ø£Ø¹Ù…Ø¯Ø©';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['ar-SA']);

})(jQuery);

/**
 * Bootstrap Table Catalan translation
 * Authors: Marc Pina<iwalkalone69@gmail.com>
 *          Claudi Martinez<claudix.kernel@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['ca-ES'] = {
        formatLoadingMessage: function () {
            return 'Espereu, si us plau...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' resultats per pÃ gina';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Mostrant de ' + pageFrom + ' fins ' + pageTo + ' - total ' + totalRows + ' resultats';
        },
        formatSearch: function () {
            return 'Cerca';
        },
        formatNoMatches: function () {
            return 'No s\'han trobat resultats';
        },
        formatPaginationSwitch: function () {
            return 'Amaga/Mostra paginaciÃ³';
        },
        formatRefresh: function () {
            return 'Refresca';
        },
        formatToggle: function () {
            return 'Alterna formataciÃ³';
        },
        formatColumns: function () {
            return 'Columnes';
        },
        formatAllRows: function () {
            return 'Tots';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['ca-ES']);

})(jQuery);

/**
 * Bootstrap Table Czech translation
 * Author: Lukas Kral (monarcha@seznam.cz)
 * Author: Jakub Svestka <svestka1999@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['cs-CZ'] = {
        formatLoadingMessage: function () {
            return 'ÄŒekejte, prosÃ­m...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' poloÅ¾ek na strÃ¡nku';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Zobrazena ' + pageFrom + '. - ' + pageTo + '. poloÅ¾ka z celkovÃ½ch ' + totalRows;
        },
        formatSearch: function () {
            return 'VyhledÃ¡vÃ¡nÃ­';
        },
        formatNoMatches: function () {
            return 'Nenalezena Å¾Ã¡dnÃ¡ vyhovujÃ­cÃ­ poloÅ¾ka';
        },
        formatPaginationSwitch: function () {
            return 'SkrÃ½t/Zobrazit strÃ¡nkovÃ¡nÃ­';
        },
        formatRefresh: function () {
            return 'Aktualizovat';
        },
        formatToggle: function () {
            return 'PÅ™epni';
        },
        formatColumns: function () {
            return 'Sloupce';
        },
        formatAllRows: function () {
            return 'VÅ¡e';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['cs-CZ']);

})(jQuery);

/**
 * Bootstrap Table danish translation
 * Author: Your Name Jan Borup Coyle, github@coyle.dk
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['da-DK'] = {
        formatLoadingMessage: function () {
            return 'IndlÃ¦ser, vent venligst...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' poster pr side';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Viser ' + pageFrom + ' til ' + pageTo + ' af ' + totalRows + ' rÃ¦kker';
        },
        formatSearch: function () {
            return 'SÃ¸g';
        },
        formatNoMatches: function () {
            return 'Ingen poster fundet';
        },
        formatRefresh: function () {
            return 'Opdater';
        },
        formatToggle: function () {
            return 'Skift';
        },
        formatColumns: function () {
            return 'Kolonner';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['da-DK']);

})(jQuery);
/**
* Bootstrap Table German translation
* Author: Paul Mohr - Sopamo<p.mohr@sopamo.de>
*/
(function ($) {
  'use strict';

  $.fn.bootstrapTable.locales['de-DE'] = {
    formatLoadingMessage: function () {
      return 'Lade, bitte warten...';
    },
    formatRecordsPerPage: function (pageNumber) {
      return pageNumber + ' EintrÃ¤ge pro Seite';
    },
    formatShowingRows: function (pageFrom, pageTo, totalRows) {
      return 'Zeige ' + pageFrom + ' bis ' + pageTo + ' von ' + totalRows + ' Zeile' + ((totalRows > 1) ? "n" : "");
    },
    formatSearch: function () {
      return 'Suchen';
    },
    formatNoMatches: function () {
      return 'Keine passenden Ergebnisse gefunden';
    },
    formatRefresh: function () {
      return 'Neu laden';
    },
    formatToggle: function () {
      return 'Umschalten';
    },
    formatColumns: function () {
      return 'Spalten';
    }
  };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['de-DE']);

})(jQuery);

/**
 * Bootstrap Table Greek translation
 * Author: giannisdallas
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['el-GR'] = {
        formatLoadingMessage: function () {
            return 'Î¦Î¿Ï�Ï„ÏŽÎ½ÎµÎ¹, Ï€Î±Ï�Î±ÎºÎ±Î»ÏŽ Ï€ÎµÏ�Î¹Î¼Î­Î½ÎµÏ„Îµ...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' Î±Ï€Î¿Ï„ÎµÎ»Î­ÏƒÎ¼Î±Ï„Î± Î±Î½Î¬ ÏƒÎµÎ»Î¯Î´Î±';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Î•Î¼Ï†Î±Î½Î¯Î¶Î¿Î½Ï„Î±Î¹ Î±Ï€ÏŒ Ï„Î·Î½ ' + pageFrom + ' Ï‰Ï‚ Ï„Î·Î½ ' + pageTo + ' Î±Ï€ÏŒ ÏƒÏ�Î½Î¿Î»Î¿ ' + totalRows + ' ÏƒÎµÎ¹Ï�ÏŽÎ½';
        },
        formatSearch: function () {
            return 'Î‘Î½Î±Î¶Î·Ï„Î®ÏƒÏ„Îµ';
        },
        formatNoMatches: function () {
            return 'Î”ÎµÎ½ Î²Ï�Î­Î¸Î·ÎºÎ±Î½ Î±Ï€Î¿Ï„ÎµÎ»Î­ÏƒÎ¼Î±Ï„Î±';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['el-GR']);

})(jQuery);

/**
 * Bootstrap Table English translation
 * Author: Zhixin Wen<wenzhixin2010@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['en-US'] = {
        formatLoadingMessage: function () {
            return 'Loading, please wait...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' rows per page';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Showing ' + pageFrom + ' to ' + pageTo + ' of ' + totalRows + ' rows';
        },
        formatSearch: function () {
            return 'Search';
        },
        formatNoMatches: function () {
            return 'No matching records found';
        },
        formatPaginationSwitch: function () {
            return 'Hide/Show pagination';
        },
        formatRefresh: function () {
            return 'Refresh';
        },
        formatToggle: function () {
            return 'Toggle';
        },
        formatColumns: function () {
            return 'Columns';
        },
        formatAllRows: function () {
            return 'All';
        },
        formatExport: function () {
            return 'Export data';
        },
        formatClearFilters: function () {
            return 'Clear filters';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['en-US']);

})(jQuery);

/**
 * Bootstrap Table Spanish (Argentina) translation
 * Author: Felix Vera (felix.vera@gmail.com)
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['es-AR'] = {
        formatLoadingMessage: function () {
            return 'Cargando, espere por favor...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' registros por pÃ¡gina';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Mostrando ' + pageFrom + ' a ' + pageTo + ' de ' + totalRows + ' filas';
        },
        formatSearch: function () {
            return 'Buscar';
        },
        formatNoMatches: function () {
            return 'No se encontraron registros';
        },
        formatAllRows: function () {
            return 'Todo';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['es-AR']);

})(jQuery);
/**
 * Bootstrap Table Spanish (Costa Rica) translation
 * Author: Dennis HernÃ¡ndez (http://djhvscf.github.io/Blog/)
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['es-CR'] = {
        formatLoadingMessage: function () {
            return 'Cargando, por favor espere...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' registros por pÃ¡gina';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Mostrando de ' + pageFrom + ' a ' + pageTo + ' registros de ' + totalRows + ' registros en total';
        },
        formatSearch: function () {
            return 'Buscar';
        },
        formatNoMatches: function () {
            return 'No se encontraron registros';
        },
        formatRefresh: function () {
            return 'Refrescar';
        },
        formatToggle: function () {
            return 'Alternar';
        },
        formatColumns: function () {
            return 'Columnas';
        },
        formatAllRows: function () {
            return 'Todo';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['es-CR']);

})(jQuery);

/**
 * Bootstrap Table Spanish Spain translation
 * Author: Marc Pina<iwalkalone69@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['es-ES'] = {
        formatLoadingMessage: function () {
            return 'Por favor espere...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' resultados por pÃ¡gina';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Mostrando desde ' + pageFrom + ' hasta ' + pageTo + ' - En total ' + totalRows + ' resultados';
        },
        formatSearch: function () {
            return 'Buscar';
        },
        formatNoMatches: function () {
            return 'No se encontraron resultados';
        },
        formatPaginationSwitch: function () {
            return 'Ocultar/Mostrar paginaciÃ³n';
        },
        formatRefresh: function () {
            return 'Refrescar';
        },
        formatToggle: function () {
            return 'Ocultar/Mostrar';
        },
        formatColumns: function () {
            return 'Columnas';
        },
        formatAllRows: function () {
            return 'Todos';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['es-ES']);

})(jQuery);

/**
 * Bootstrap Table Spanish (MÃ©xico) translation (Obtenido de traducciÃ³n de Argentina)
 * Author: Felix Vera (felix.vera@gmail.com) 
 * Copiado: Mauricio Vera (mauricioa.vera@gmail.com)
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['es-MX'] = {
        formatLoadingMessage: function () {
            return 'Cargando, espere por favor...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' registros por pÃ¡gina';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Mostrando ' + pageFrom + ' a ' + pageTo + ' de ' + totalRows + ' filas';
        },
        formatSearch: function () {
            return 'Buscar';
        },
        formatNoMatches: function () {
            return 'No se encontraron registros';
        },
        formatAllRows: function () {
            return 'Todo';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['es-MX']);

})(jQuery);

/**
 * Bootstrap Table Spanish (Nicaragua) translation
 * Author: Dennis HernÃ¡ndez (http://djhvscf.github.io/Blog/)
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['es-NI'] = {
        formatLoadingMessage: function () {
            return 'Cargando, por favor espere...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' registros por pÃ¡gina';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Mostrando de ' + pageFrom + ' a ' + pageTo + ' registros de ' + totalRows + ' registros en total';
        },
        formatSearch: function () {
            return 'Buscar';
        },
        formatNoMatches: function () {
            return 'No se encontraron registros';
        },
        formatRefresh: function () {
            return 'Refrescar';
        },
        formatToggle: function () {
            return 'Alternar';
        },
        formatColumns: function () {
            return 'Columnas';
        },
        formatAllRows: function () {
            return 'Todo';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['es-NI']);

})(jQuery);

/**
 * Bootstrap Table Spanish (EspaÃ±a) translation
 * Author: Antonio PÃ©rez <anpegar@gmail.com>
 */
 (function ($) {
    'use strict';
    
    $.fn.bootstrapTable.locales['es-SP'] = {
        formatLoadingMessage: function () {
            return 'Cargando, por favor espera...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' registros por p&#225;gina.';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return pageFrom + ' - ' + pageTo + ' de ' + totalRows + ' registros.';
        },
        formatSearch: function () {
            return 'Buscar';
        },
        formatNoMatches: function () {
            return 'No se han encontrado registros.';
        },
        formatRefresh: function () {
            return 'Actualizar';
        },
        formatToggle: function () {
            return 'Alternar';
        },
        formatColumns: function () {
            return 'Columnas';
        },
        formatAllRows: function () {
            return 'Todo';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['es-SP']);

})(jQuery);
/**
 * Bootstrap Table Estonian translation
 * Author: kristjan@logist.it>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['et-EE'] = {
        formatLoadingMessage: function () {
            return 'PÃ¤ring kÃ¤ib, palun oota...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' rida lehe kohta';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'NÃ¤itan tulemusi ' + pageFrom + ' kuni ' + pageTo + ' - kokku ' + totalRows + ' tulemust';
        },
        formatSearch: function () {
            return 'Otsi';
        },
        formatNoMatches: function () {
            return 'PÃ¤ringu tingimustele ei vastanud Ã¼htegi tulemust';
        },
        formatPaginationSwitch: function () {
            return 'NÃ¤ita/Peida lehtedeks jagamine';
        },
        formatRefresh: function () {
            return 'VÃ¤rskenda';
        },
        formatToggle: function () {
            return 'LÃ¼lita';
        },
        formatColumns: function () {
            return 'Veerud';
        },
        formatAllRows: function () {
            return 'KÃµik';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['et-EE']);

})(jQuery);
/**
 * Bootstrap Table Persian translation
 * Author: MJ Vakili <mjv.1989@Gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['fa-IR'] = {
        formatLoadingMessage: function () {
            return 'Ø¯Ø± Ø­Ø§Ù„ Ø¨Ø§Ø±Ú¯Ø°Ø§Ø±ÛŒ, Ù„Ø·Ù�Ø§ ØµØ¨Ø± Ú©Ù†ÛŒØ¯...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' Ø±Ú©ÙˆØ±Ø¯ Ø¯Ø± ØµÙ�Ø­Ù‡';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Ù†Ù…Ø§ÛŒØ´ ' + pageFrom + ' ØªØ§ ' + pageTo + ' Ø§Ø² ' + totalRows + ' Ø±Ø¯ÛŒÙ�';
        },
        formatSearch: function () {
            return 'Ø¬Ø³ØªØ¬Ùˆ';
        },
        formatNoMatches: function () {
            return 'Ø±Ú©ÙˆØ±Ø¯ÛŒ ÛŒØ§Ù�Øª Ù†Ø´Ø¯.';
        },
        formatPaginationSwitch: function () {
            return 'Ù†Ù…Ø§ÛŒØ´/Ù…Ø®Ù�ÛŒ ØµÙ�Ø­Ù‡ Ø¨Ù†Ø¯ÛŒ';
        },
        formatRefresh: function () {
            return 'Ø¨Ù‡ Ø±ÙˆØ² Ø±Ø³Ø§Ù†ÛŒ';
        },
        formatToggle: function () {
            return 'ØªØºÛŒÛŒØ± Ù†Ù…Ø§ÛŒØ´';
        },
        formatColumns: function () {
            return 'Ø³Ø·Ø± Ù‡Ø§';
        },
        formatAllRows: function () {
            return 'Ù‡Ù…Ù‡';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['fa-IR']);

})(jQuery);
/**
 * Bootstrap Table French (Belgium) translation
 * Author: Julien Bisconti (julien.bisconti@gmail.com)
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['fr-BE'] = {
        formatLoadingMessage: function () {
            return 'Chargement en cours...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' entrÃ©es par page';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Affiche de' + pageFrom + ' Ã  ' + pageTo + ' sur ' + totalRows + ' lignes';
        },
        formatSearch: function () {
            return 'Recherche';
        },
        formatNoMatches: function () {
            return 'Pas de fichiers trouvÃ©s';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['fr-BE']);

})(jQuery);

/**
 * Bootstrap Table French (France) translation
 * Author: Dennis HernÃ¡ndez (http://djhvscf.github.io/Blog/)
 * Modification: Tidalf (https://github.com/TidalfFR)
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['fr-FR'] = {
        formatLoadingMessage: function () {
            return 'Chargement en cours, patientez, sÂ´il vous plaÃ®t ...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' lignes par page';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Affichage des lignes ' + pageFrom + ' Ã  ' + pageTo + ' sur ' + totalRows + ' lignes au total';
        },
        formatSearch: function () {
            return 'Rechercher';
        },
        formatNoMatches: function () {
            return 'Aucun rÃ©sultat trouvÃ©';
        },
        formatRefresh: function () {
            return 'RafraÃ®chir';
        },
        formatToggle: function () {
            return 'Alterner';
        },
        formatColumns: function () {
            return 'Colonnes';
        },
        formatAllRows: function () {
            return 'Tous';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['fr-FR']);

})(jQuery);

/**
 * Bootstrap Table Hebrew translation
 * Author: legshooter
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['he-IL'] = {
        formatLoadingMessage: function () {
            return '×˜×•×¢×Ÿ, × ×� ×œ×”×ž×ª×™×Ÿ...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' ×©×•×¨×•×ª ×‘×¢×ž×•×“';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return '×ž×¦×™×’ ' + pageFrom + ' ×¢×“ ' + pageTo + ' ×ž-' + totalRows + ' ×©×•×¨×•×ª';
        },
        formatSearch: function () {
            return '×—×™×¤×•×©';
        },
        formatNoMatches: function () {
            return '×œ×� × ×ž×¦×�×• ×¨×©×•×ž×•×ª ×ª×•×�×ž×•×ª';
        },
        formatPaginationSwitch: function () {
            return '×”×¡×ª×¨/×”×¦×’ ×ž×¡×¤×•×¨ ×“×¤×™×�';
        },
        formatRefresh: function () {
            return '×¨×¢× ×Ÿ';
        },
        formatToggle: function () {
            return '×”×—×œ×£ ×ª×¦×•×’×”';
        },
        formatColumns: function () {
            return '×¢×ž×•×“×•×ª';
        },
        formatAllRows: function () {
            return '×”×›×œ';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['he-IL']);

})(jQuery);

/**
 * Bootstrap Table Croatian translation
 * Author: Petra Å trbenac (petra.strbenac@gmail.com)
 * Author: Petra Å trbenac (petra.strbenac@gmail.com)
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['hr-HR'] = {
        formatLoadingMessage: function () {
            return 'Molimo priÄ�ekajte ...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' broj zapisa po stranici';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Prikazujem ' + pageFrom + '. - ' + pageTo + '. od ukupnog broja zapisa ' + totalRows;
        },
        formatSearch: function () {
            return 'PretraÅ¾i';
        },
        formatNoMatches: function () {
            return 'Nije pronaÄ‘en niti jedan zapis';
        },
        formatPaginationSwitch: function () {
            return 'PrikaÅ¾i/sakrij stranice';
        },
        formatRefresh: function () {
            return 'OsvjeÅ¾i';
        },
        formatToggle: function () {
            return 'Promijeni prikaz';
        },
        formatColumns: function () {
            return 'Kolone';
        },
        formatAllRows: function () {
            return 'Sve';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['hr-HR']);

})(jQuery);

/**
 * Bootstrap Table Hungarian translation
 * Author: Nagy Gergely <info@nagygergely.eu>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['hu-HU'] = {
        formatLoadingMessage: function () {
            return 'BetÃ¶ltÃ©s, kÃ©rem vÃ¡rjon...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' rekord per oldal';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'MegjelenÃ­tve ' + pageFrom + ' - ' + pageTo + ' / ' + totalRows + ' Ã¶sszesen';
        },
        formatSearch: function () {
            return 'KeresÃ©s';
        },
        formatNoMatches: function () {
            return 'Nincs talÃ¡lat';
        },
        formatPaginationSwitch: function () {
            return 'LapozÃ³ elrejtÃ©se/megjelenÃ­tÃ©se';
        },
        formatRefresh: function () {
            return 'FrissÃ­tÃ©s';
        },
        formatToggle: function () {
            return 'Ã–sszecsuk/Kinyit';
        },
        formatColumns: function () {
            return 'Oszlopok';
        },
        formatAllRows: function () {
            return 'Ã–sszes';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['hu-HU']);

})(jQuery);

/**
 * Bootstrap Table Italian translation
 * Author: Davide Renzi<davide.renzi@gmail.com>
 * Author: Davide Borsatto <davide.borsatto@gmail.com>
 * Author: Alessio Felicioni <alessio.felicioni@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['it-IT'] = {
        formatLoadingMessage: function () {
            return 'Caricamento in corso...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' elementi per pagina';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Pagina ' + pageFrom + ' di ' + pageTo + ' (' + totalRows + ' elementi)';
        },
        formatSearch: function () {
            return 'Cerca';
        },
        formatNoMatches: function () {
            return 'Nessun elemento trovato';
        },
        formatRefresh: function () {
            return 'Aggiorna';
        },
        formatToggle: function () {
            return 'Alterna';
        },
        formatColumns: function () {
            return 'Colonne';
        },
        formatAllRows: function () {
            return 'Tutto';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['it-IT']);

})(jQuery);

/**
 * Bootstrap Table Japanese translation
 * Author: Azamshul Azizy <azamshul@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['ja-JP'] = {
        formatLoadingMessage: function () {
            return 'èª­ã�¿è¾¼ã�¿ä¸­ã�§ã�™ã€‚å°‘ã€…ã�Šå¾…ã�¡ã��ã� ã�•ã�„ã€‚';
        },
        formatRecordsPerPage: function (pageNumber) {
            return 'ãƒšãƒ¼ã‚¸å½“ã�Ÿã‚Šæœ€å¤§' + pageNumber + 'ä»¶';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'å…¨' + totalRows + 'ä»¶ã�‹ã‚‰ã€�'+ pageFrom + 'ã�‹ã‚‰' + pageTo + 'ä»¶ç›®ã�¾ã�§è¡¨ç¤ºã�—ã�¦ã�„ã�¾ã�™';
        },
        formatSearch: function () {
            return 'æ¤œç´¢';
        },
        formatNoMatches: function () {
            return 'è©²å½“ã�™ã‚‹ãƒ¬ã‚³ãƒ¼ãƒ‰ã�Œè¦‹ã�¤ã�‹ã‚Šã�¾ã�›ã‚“';
        },
        formatPaginationSwitch: function () {
            return 'ãƒšãƒ¼ã‚¸æ•°ã‚’è¡¨ç¤ºãƒ»é�žè¡¨ç¤º';
        },
        formatRefresh: function () {
            return 'æ›´æ–°';
        },
        formatToggle: function () {
            return 'ãƒˆã‚°ãƒ«';
        },
        formatColumns: function () {
            return 'åˆ—';
        },
        formatAllRows: function () {
            return 'ã�™ã�¹ã�¦';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['ja-JP']);

})(jQuery);
/**
 * Bootstrap Table Georgian translation
 * Author: Levan Lotuashvili <l.lotuashvili@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['ka-GE'] = {
        formatLoadingMessage: function() {
            return 'áƒ˜áƒ¢áƒ•áƒ˜áƒ áƒ—áƒ”áƒ‘áƒ�, áƒ’áƒ—áƒ®áƒ�áƒ•áƒ— áƒ›áƒ�áƒ˜áƒªáƒ�áƒ“áƒ�áƒ—...';
        },
        formatRecordsPerPage: function(pageNumber) {
            return pageNumber + ' áƒ©áƒ�áƒœáƒ�áƒ¬áƒ”áƒ áƒ˜ áƒ—áƒ˜áƒ—áƒ� áƒ’áƒ•áƒ”áƒ áƒ“áƒ–áƒ”';
        },
        formatShowingRows: function(pageFrom, pageTo, totalRows) {
            return 'áƒœáƒ�áƒ©áƒ•áƒ”áƒœáƒ”áƒ‘áƒ˜áƒ� ' + pageFrom + '-áƒ“áƒ�áƒœ ' + pageTo + '-áƒ›áƒ“áƒ” áƒ©áƒ�áƒœáƒ�áƒ¬áƒ”áƒ áƒ˜ áƒ¯áƒ�áƒ›áƒ£áƒ áƒ˜ ' + totalRows + '-áƒ“áƒ�áƒœ';
        },
        formatSearch: function() {
            return 'áƒ«áƒ”áƒ‘áƒœáƒ�';
        },
        formatNoMatches: function() {
            return 'áƒ›áƒ�áƒœáƒ�áƒªáƒ”áƒ›áƒ”áƒ‘áƒ˜ áƒ�áƒ  áƒ�áƒ áƒ˜áƒ¡';
        },
        formatPaginationSwitch: function() {
            return 'áƒ’áƒ•áƒ”áƒ áƒ“áƒ”áƒ‘áƒ˜áƒ¡ áƒ’áƒ�áƒ“áƒ�áƒ›áƒ áƒ—áƒ•áƒ”áƒšáƒ˜áƒ¡ áƒ“áƒ�áƒ›áƒ�áƒšáƒ•áƒ�/áƒ’áƒ�áƒ›áƒ�áƒ©áƒ”áƒœáƒ�';
        },
        formatRefresh: function() {
            return 'áƒ’áƒ�áƒœáƒ�áƒ®áƒšáƒ”áƒ‘áƒ�';
        },
        formatToggle: function() {
            return 'áƒ©áƒ�áƒ áƒ—áƒ•áƒ�/áƒ’áƒ�áƒ›áƒ�áƒ áƒ—áƒ•áƒ�';
        },
        formatColumns: function() {
            return 'áƒ¡áƒ•áƒ”áƒ¢áƒ”áƒ‘áƒ˜';
        }
    };
    
    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['ka-GE']);

})(jQuery);

/**
 * Bootstrap Table Korean translation
 * Author: Yi Tae-Hyeong (jsonobject@gmail.com)
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['ko-KR'] = {
        formatLoadingMessage: function () {
            return 'ë�°ì�´í„°ë¥¼ ë¶ˆëŸ¬ì˜¤ëŠ” ì¤‘ìž…ë‹ˆë‹¤...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return 'íŽ˜ì�´ì§€ ë‹¹ ' + pageNumber + 'ê°œ ë�°ì�´í„° ì¶œë ¥';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'ì „ì²´ ' + totalRows + 'ê°œ ì¤‘ ' + pageFrom + '~' + pageTo + 'ë²ˆì§¸ ë�°ì�´í„° ì¶œë ¥,';
        },
        formatSearch: function () {
            return 'ê²€ìƒ‰';
        },
        formatNoMatches: function () {
            return 'ì¡°íšŒë�œ ë�°ì�´í„°ê°€ ì—†ìŠµë‹ˆë‹¤.';
        },
        formatRefresh: function () {
            return 'ìƒˆë¡œ ê³ ì¹¨';
        },
        formatToggle: function () {
            return 'ì „í™˜';
        },
        formatColumns: function () {
            return 'ì»¬ëŸ¼ í•„í„°ë§�';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['ko-KR']);

})(jQuery);
/**
 * Bootstrap Table Malay translation
 * Author: Azamshul Azizy <azamshul@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['ms-MY'] = {
        formatLoadingMessage: function () {
            return 'Permintaan sedang dimuatkan. Sila tunggu sebentar...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' rekod setiap muka surat';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Sedang memaparkan rekod ' + pageFrom + ' hingga ' + pageTo + ' daripada jumlah ' + totalRows + ' rekod';
        },
        formatSearch: function () {
            return 'Cari';
        },
        formatNoMatches: function () {
            return 'Tiada rekod yang menyamai permintaan';
        },
        formatPaginationSwitch: function () {
            return 'Tunjuk/sembunyi muka surat';
        },
        formatRefresh: function () {
            return 'Muatsemula';
        },
        formatToggle: function () {
            return 'Tukar';
        },
        formatColumns: function () {
            return 'Lajur';
        },
        formatAllRows: function () {
            return 'Semua';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['ms-MY']);

})(jQuery);

/**
 * Bootstrap Table norwegian translation
 * Author: Jim NordbÃ¸, jim@nordb.no
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['nb-NO'] = {
        formatLoadingMessage: function () {
            return 'Oppdaterer, vennligst vent...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' poster pr side';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Viser ' + pageFrom + ' til ' + pageTo + ' av ' + totalRows + ' rekker';
        },
        formatSearch: function () {
            return 'SÃ¸k';
        },
        formatNoMatches: function () {
            return 'Ingen poster funnet';
        },
        formatRefresh: function () {
            return 'Oppdater';
        },
        formatToggle: function () {
            return 'Endre';
        },
        formatColumns: function () {
            return 'Kolonner';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['nb-NO']);

})(jQuery);
/**
 * Bootstrap Table Dutch translation
 * Author: Your Name <info@a2hankes.nl>
 */
(function($) {
    'use strict';

    $.fn.bootstrapTable.locales['nl-NL'] = {
        formatLoadingMessage: function() {
            return 'Laden, even geduld...';
        },
        formatRecordsPerPage: function(pageNumber) {
            return pageNumber + ' records per pagina';
        },
        formatShowingRows: function(pageFrom, pageTo, totalRows) {
            return 'Toon ' + pageFrom + ' tot ' + pageTo + ' van ' + totalRows + ' record' + ((totalRows > 1) ? 's' : '');
        },
        formatDetailPagination: function(totalRows) {
            return 'Toon ' + totalRows + ' record' + ((totalRows > 1) ? 's' : '');
        },
        formatSearch: function() {
            return 'Zoeken';
        },
        formatNoMatches: function() {
            return 'Geen resultaten gevonden';
        },
        formatRefresh: function() {
            return 'Vernieuwen';
        },
        formatToggle: function() {
            return 'Omschakelen';
        },
        formatColumns: function() {
            return 'Kolommen';
        },
        formatAllRows: function() {
            return 'Alle';
        },
        formatPaginationSwitch: function() {
            return 'Verberg/Toon paginatie';
        },
        formatExport: function() {
            return 'Exporteer data';
        },
        formatClearFilters: function() {
            return 'Verwijder filters';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['nl-NL']);

})(jQuery);

/**
 * Bootstrap Table Polish translation
 * Author: zergu <michal.zagdan @ gmail com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['pl-PL'] = {
        formatLoadingMessage: function () {
            return 'Å�adowanie, proszÄ™ czekaÄ‡...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' rekordÃ³w na stronÄ™';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'WyÅ›wietlanie rekordÃ³w od ' + pageFrom + ' do ' + pageTo + ' z ' + totalRows;
        },
        formatSearch: function () {
            return 'Szukaj';
        },
        formatNoMatches: function () {
            return 'Niestety, nic nie znaleziono';
        },
        formatRefresh: function () {
            return 'OdÅ›wieÅ¼';
        },
        formatToggle: function () {
            return 'PrzeÅ‚Ä…cz';
        },
        formatColumns: function () {
            return 'Kolumny';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['pl-PL']);

})(jQuery);

/**
 * Bootstrap Table Brazilian Portuguese Translation
 * Author: Eduardo Cerqueira<egcerqueira@gmail.com>
 * Update: JoÃ£o Mello<jmello@hotmail.com.br>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['pt-BR'] = {
        formatLoadingMessage: function () {
            return 'Carregando, aguarde...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' registros por pÃ¡gina';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Exibindo ' + pageFrom + ' atÃ© ' + pageTo + ' de ' + totalRows + ' linhas';
        },
        formatSearch: function () { 
            return 'Pesquisar';
        },
        formatRefresh: function () { 
            return 'Recarregar';
        },
        formatToggle: function () { 
            return 'Alternar';
        },
        formatColumns: function () { 
            return 'Colunas';
        },
        formatPaginationSwitch: function () { 
            return 'Ocultar/Exibir paginaÃ§Ã£o';
        },
        formatNoMatches: function () {
            return 'Nenhum registro encontrado';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['pt-BR']);

})(jQuery);

/**
 * Bootstrap Table Portuguese Portugal Translation
 * Author: Burnspirit<burnspirit@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['pt-PT'] = {
        formatLoadingMessage: function () {
            return 'A carregar, por favor aguarde...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' registos por p&aacute;gina';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'A mostrar ' + pageFrom + ' at&eacute; ' + pageTo + ' de ' + totalRows + ' linhas';
        },
        formatSearch: function () {
            return 'Pesquisa';
        },
        formatNoMatches: function () {
            return 'Nenhum registo encontrado';
        },
        formatPaginationSwitch: function () {
            return 'Esconder/Mostrar pagina&ccedil&atilde;o';
        },
        formatRefresh: function () {
            return 'Atualizar';
        },
        formatToggle: function () {
            return 'Alternar';
        },
        formatColumns: function () {
            return 'Colunas';
        },
        formatAllRows: function () {
            return 'Tudo';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['pt-PT']);

})(jQuery);

/**
 * Bootstrap Table Romanian translation
 * Author: cristake <cristianiosif@me.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['ro-RO'] = {
        formatLoadingMessage: function () {
            return 'Se incarca, va rugam asteptati...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' inregistrari pe pagina';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Arata de la ' + pageFrom + ' pana la ' + pageTo + ' din ' + totalRows + ' randuri';
        },
        formatSearch: function () {
            return 'Cauta';
        },
        formatNoMatches: function () {
            return 'Nu au fost gasite inregistrari';
        },
        formatPaginationSwitch: function () {
            return 'Ascunde/Arata paginatia';
        },
        formatRefresh: function () {
            return 'Reincarca';
        },
        formatToggle: function () {
            return 'Comuta';
        },
        formatColumns: function () {
            return 'Coloane';
        },
        formatAllRows: function () {
            return 'Toate';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['ro-RO']);

})(jQuery);
/**
 * Bootstrap Table Russian translation
 * Author: Dunaevsky Maxim <dunmaksim@yandex.ru>
 */
(function ($) {
    'use strict';
    $.fn.bootstrapTable.locales['ru-RU'] = {
        formatLoadingMessage: function () {
            return 'ÐŸÐ¾Ð¶Ð°Ð»ÑƒÐ¹Ñ�Ñ‚Ð°, Ð¿Ð¾Ð´Ð¾Ð¶Ð´Ð¸Ñ‚Ðµ, Ð¸Ð´Ñ‘Ñ‚ Ð·Ð°Ð³Ñ€ÑƒÐ·ÐºÐ°...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' Ð·Ð°Ð¿Ð¸Ñ�ÐµÐ¹ Ð½Ð° Ñ�Ñ‚Ñ€Ð°Ð½Ð¸Ñ†Ñƒ';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Ð—Ð°Ð¿Ð¸Ñ�Ð¸ Ñ� ' + pageFrom + ' Ð¿Ð¾ ' + pageTo + ' Ð¸Ð· ' + totalRows;
        },
        formatSearch: function () {
            return 'ÐŸÐ¾Ð¸Ñ�Ðº';
        },
        formatNoMatches: function () {
            return 'Ð�Ð¸Ñ‡ÐµÐ³Ð¾ Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½Ð¾';
        },
        formatRefresh: function () {
            return 'ÐžÐ±Ð½Ð¾Ð²Ð¸Ñ‚ÑŒ';
        },
        formatToggle: function () {
            return 'ÐŸÐµÑ€ÐµÐºÐ»ÑŽÑ‡Ð¸Ñ‚ÑŒ';
        },
        formatColumns: function () {
            return 'ÐšÐ¾Ð»Ð¾Ð½ÐºÐ¸';
        },
        formatClearFilters: function () {
            return 'ÐžÑ‡Ð¸Ñ�Ñ‚Ð¸Ñ‚ÑŒ Ñ„Ð¸Ð»ÑŒÑ‚Ñ€Ñ‹';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['ru-RU']);

})(jQuery);

/**
 * Bootstrap Table Slovak translation
 * Author: Jozef DÃºc<jozef.d13@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['sk-SK'] = {
        formatLoadingMessage: function () {
            return 'ProsÃ­m Ä�akajte ...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' zÃ¡znamov na stranu';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'ZobrazenÃ¡ ' + pageFrom + '. - ' + pageTo + '. poloÅ¾ka z celkovÃ½ch ' + totalRows;
        },
        formatSearch: function () {
            return 'VyhÄ¾adÃ¡vanie';
        },
        formatNoMatches: function () {
            return 'NenÃ¡jdenÃ¡ Å¾iadna vyhovujÃºca poloÅ¾ka';
        },
        formatRefresh: function () {
            return 'ObnoviÅ¥';
        },
        formatToggle: function () {
            return 'Prepni';
        },
        formatColumns: function () {
            return 'StÄºpce';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['sk-SK']);

})(jQuery);

/**
 * Bootstrap Table Swedish translation
 * Author: C Bratt <bratt@inix.se>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['sv-SE'] = {
        formatLoadingMessage: function () {
            return 'Laddar, vÃ¤nligen vÃ¤nta...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' rader per sida';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Visa ' + pageFrom + ' till ' + pageTo + ' av ' + totalRows + ' rader';
        },
        formatSearch: function () {
            return 'SÃ¶k';
        },
        formatNoMatches: function () {
            return 'Inga matchande resultat funna.';
        },
        formatRefresh: function () {
            return 'Uppdatera';
        },
        formatToggle: function () {
            return 'Skifta';
        },
        formatColumns: function () {
            return 'kolumn';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['sv-SE']);

})(jQuery);

/**
 * Bootstrap Table Thai translation
 * Author: Monchai S.<monchais@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['th-TH'] = {
        formatLoadingMessage: function () {
            return 'à¸�à¸³à¸¥à¸±à¸‡à¹‚à¸«à¸¥à¸”à¸‚à¹‰à¸­à¸¡à¸¹à¸¥, à¸�à¸£à¸¸à¸“à¸²à¸£à¸­à¸ªà¸±à¸�à¸„à¸£à¸¹à¹ˆ...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' à¸£à¸²à¸¢à¸�à¸²à¸£à¸•à¹ˆà¸­à¸«à¸™à¹‰à¸²';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'à¸£à¸²à¸¢à¸�à¸²à¸£à¸—à¸µà¹ˆ ' + pageFrom + ' à¸–à¸¶à¸‡ ' + pageTo + ' à¸ˆà¸²à¸�à¸—à¸±à¹‰à¸‡à¸«à¸¡à¸” ' + totalRows + ' à¸£à¸²à¸¢à¸�à¸²à¸£';
        },
        formatSearch: function () {
            return 'à¸„à¹‰à¸™à¸«à¸²';
        },
        formatNoMatches: function () {
            return 'à¹„à¸¡à¹ˆà¸žà¸šà¸£à¸²à¸¢à¸�à¸²à¸£à¸—à¸µà¹ˆà¸„à¹‰à¸™à¸«à¸² !';
        },
        formatRefresh: function () {
            return 'à¸£à¸µà¹€à¸Ÿà¸£à¸ª';
        },
        formatToggle: function () {
            return 'à¸ªà¸¥à¸±à¸šà¸¡à¸¸à¸¡à¸¡à¸­à¸‡';
        },
        formatColumns: function () {
            return 'à¸„à¸­à¸¥à¸±à¸¡à¸™à¹Œ';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['th-TH']);

})(jQuery);

/**
 * Bootstrap Table Turkish translation
 * Author: Emin Åžen
 * Author: Sercan Cakir <srcnckr@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['tr-TR'] = {
        formatLoadingMessage: function () {
            return 'YÃ¼kleniyor, lÃ¼tfen bekleyin...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return 'Sayfa baÅŸÄ±na ' + pageNumber + ' kayÄ±t.';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return totalRows + ' kayÄ±ttan ' + pageFrom + '-' + pageTo + ' arasÄ± gÃ¶steriliyor.';
        },
        formatSearch: function () {
            return 'Ara';
        },
        formatNoMatches: function () {
            return 'EÅŸleÅŸen kayÄ±t bulunamadÄ±.';
        },
        formatRefresh: function () {
            return 'Yenile';
        },
        formatToggle: function () {
            return 'DeÄŸiÅŸtir';
        },
        formatColumns: function () {
            return 'SÃ¼tunlar';
        },
        formatAllRows: function () {
            return 'TÃ¼m SatÄ±rlar';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['tr-TR']);

})(jQuery);

/**
 * Bootstrap Table Ukrainian translation
 * Author: Vitaliy Timchenko <vitaliy.timchenko@gmail.com>
 */
 (function ($) {
    'use strict';
    
    $.fn.bootstrapTable.locales['uk-UA'] = {
        formatLoadingMessage: function () {
            return 'Ð—Ð°Ð²Ð°Ð½Ñ‚Ð°Ð¶ÐµÐ½Ð½Ñ�, Ð±ÑƒÐ´ÑŒ Ð»Ð°Ñ�ÐºÐ°, Ð·Ð°Ñ‡ÐµÐºÐ°Ð¹Ñ‚Ðµ...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' Ð·Ð°Ð¿Ð¸Ñ�Ñ–Ð² Ð½Ð° Ñ�Ñ‚Ð¾Ñ€Ñ–Ð½ÐºÑƒ';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'ÐŸÐ¾ÐºÐ°Ð·Ð°Ð½Ð¾ Ð· ' + pageFrom + ' Ð¿Ð¾ ' + pageTo + '. Ð’Ñ�ÑŒÐ¾Ð³Ð¾: ' + totalRows;
        },
        formatSearch: function () {
            return 'ÐŸÐ¾ÑˆÑƒÐº';
        },
        formatNoMatches: function () {
            return 'Ð�Ðµ Ð·Ð½Ð°Ð¹Ð´ÐµÐ½Ð¾ Ð¶Ð¾Ð´Ð½Ð¾Ð³Ð¾ Ð·Ð°Ð¿Ð¸Ñ�Ñƒ';
        },
        formatRefresh: function () {
            return 'ÐžÐ½Ð¾Ð²Ð¸Ñ‚Ð¸';
        },
        formatToggle: function () {
            return 'Ð—Ð¼Ñ–Ð½Ð¸Ñ‚Ð¸';
        },
        formatColumns: function () {
            return 'Ð¡Ñ‚Ð¾Ð²Ð¿Ñ†Ñ–';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['uk-UA']);

})(jQuery);

/**
 * Bootstrap Table Urdu translation
 * Author: Malik <me@malikrizwan.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['ur-PK'] = {
        formatLoadingMessage: function () {
            return 'Ø¨Ø±Ø§Û“ Ù…Û�Ø±Ø¨Ø§Ù†ÛŒ Ø§Ù†ØªØ¸Ø§Ø± Ú©ÛŒØ¬Ø¦Û’';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' Ø±ÛŒÚ©Ø§Ø±ÚˆØ² Ù�ÛŒ ØµÙ�Û� ';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Ø¯ÛŒÚ©Ú¾ÛŒÚº ' + pageFrom + ' Ø³Û’ ' + pageTo + ' Ú©Û’ ' +  totalRows + 'Ø±ÛŒÚ©Ø§Ø±ÚˆØ²';
        },
        formatSearch: function () {
            return 'ØªÙ„Ø§Ø´';
        },
        formatNoMatches: function () {
            return 'Ú©ÙˆØ¦ÛŒ Ø±ÛŒÚ©Ø§Ø±Úˆ Ù†Û�ÛŒÚº Ù…Ù„Ø§';
        },
        formatRefresh: function () {
            return 'ØªØ§Ø²Û� Ú©Ø±ÛŒÚº';
        },
        formatToggle: function () {
            return 'ØªØ¨Ø¯ÛŒÙ„ Ú©Ø±ÛŒÚº';
        },
        formatColumns: function () {
            return 'Ú©Ø§Ù„Ù…';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['ur-PK']);

})(jQuery);

/**
 * Bootstrap Table Vietnamese translation
 * Author: Duc N. PHAM <pngduc@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['vi-VN'] = {
        formatLoadingMessage: function () {
            return 'Ä�ang táº£i...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' báº£n ghi má»—i trang';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Hiá»ƒn thá»‹ tá»« trang ' + pageFrom + ' Ä‘áº¿n ' + pageTo + ' cá»§a ' + totalRows + ' báº£ng ghi';
        },
        formatSearch: function () {
            return 'TÃ¬m kiáº¿m';
        },
        formatNoMatches: function () {
            return 'KhÃ´ng cÃ³ dá»¯ liá»‡u';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['vi-VN']);

})(jQuery);
/**
 * Bootstrap Table Chinese translation
 * Author: Zhixin Wen<wenzhixin2010@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['zh-CN'] = {
        formatLoadingMessage: function () {
            return 'æ­£åœ¨åŠªåŠ›åœ°åŠ è½½æ•°æ�®ä¸­ï¼Œè¯·ç¨�å€™â€¦â€¦';
        },
        formatRecordsPerPage: function (pageNumber) {
            return 'æ¯�é¡µæ˜¾ç¤º ' + pageNumber + ' æ�¡è®°å½•';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'æ˜¾ç¤ºç¬¬ ' + pageFrom + ' åˆ°ç¬¬ ' + pageTo + ' æ�¡è®°å½•ï¼Œæ€»å…± ' + totalRows + ' æ�¡è®°å½•';
        },
        formatSearch: function () {
            return 'æ�œç´¢';
        },
        formatNoMatches: function () {
            return 'æ²¡æœ‰æ‰¾åˆ°åŒ¹é…�çš„è®°å½•';
        },
        formatPaginationSwitch: function () {
            return 'éš�è—�/æ˜¾ç¤ºåˆ†é¡µ';
        },
        formatRefresh: function () {
            return 'åˆ·æ–°';
        },
        formatToggle: function () {
            return 'åˆ‡æ�¢';
        },
        formatColumns: function () {
            return 'åˆ—';
        },
        formatExport: function () {
            return 'å¯¼å‡ºæ•°æ�®';
        },
        formatClearFilters: function () {
            return 'æ¸…ç©ºè¿‡æ»¤';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['zh-CN']);

})(jQuery);

/**
 * Bootstrap Table Chinese translation
 * Author: Zhixin Wen<wenzhixin2010@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['zh-TW'] = {
        formatLoadingMessage: function () {
            return 'æ­£åœ¨åŠªåŠ›åœ°è¼‰å…¥è³‡æ–™ï¼Œè«‹ç¨�å€™â€¦â€¦';
        },
        formatRecordsPerPage: function (pageNumber) {
            return 'æ¯�é �é¡¯ç¤º ' + pageNumber + ' é …è¨˜éŒ„';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'é¡¯ç¤ºç¬¬ ' + pageFrom + ' åˆ°ç¬¬ ' + pageTo + ' é …è¨˜éŒ„ï¼Œç¸½å…± ' + totalRows + ' é …è¨˜éŒ„';
        },
        formatSearch: function () {
            return 'æ�œå°‹';
        },
        formatNoMatches: function () {
            return 'æ²’æœ‰æ‰¾åˆ°ç¬¦å�ˆçš„çµ�æžœ';
        },
        formatPaginationSwitch: function () {
            return 'éš±è—�/é¡¯ç¤ºåˆ†é �';
        },
        formatRefresh: function () {
            return 'é‡�æ–°æ•´ç�†';
        },
        formatToggle: function () {
            return 'åˆ‡æ�›';
        },
        formatColumns: function () {
            return 'åˆ—';
        }
    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['zh-TW']);

})(jQuery);
