        PROGRAM rem_flux
c
c  converts Sloan Digital Sky Survey u,g,r,i,z magnitudes into monochromatic fluxes
c  for nufnu vs nu plots 
c
        implicit none
        INTEGER*4 length, lenact
        REAL*4 nh, flux , av , m_band, m_band_err, err, a_band, Rv, y
        REAL*4 c, lambda, const, frequency, one, fm, fm_err, b, a
        CHARACTER*1 filter
        CHARACTER*256 string
        filter='U'
        nh = 3.2e20
        m_band = 14.02
        m_band_err = 0.12
c        CALL rdforn(string,length)
c        IF ( length.NE.0 ) then
c          CALL rmvlbk(string)
c          READ(string(1:lenact(string)),*)
c     &                nh, m_band , m_band_err, filter
c        ENDIF
c        call upc(filter)
c        if ( (filter(1:1).NE.'U') .AND. (filter(1:1).NE.'B') .AND.
c     &       (filter(1:1).NE.'V') .AND. (filter(1:1).NE.'R') .AND.
c     &       (filter(1:1).NE.'I') .AND. (filter(1:1).NE.'J') .AND.
c     &       (filter(1:1).NE.'H') .AND. (filter(1:1).NE.'K') )then
c         write (*,*) ' Usage : rem_flux nh mag mag_error filter '
c         write (*,*) ' e.g. : rem_flux 3.e20 14.02 0.12 U '
c         stop
c        endif
c extintion law taken from Cardelli et al. 1989 ApJ 345, 245
        Rv=3.1
        av = Rv*(-0.055+nh*1.987e-22)
        if (av.LT.0.) av=0.
        if (filter(1:1).EQ.'U') then
           lambda=3550 
           const=alog10(1810.)-23. 
        else if (filter(1:1).EQ.'B') then
           lambda=4400
           const=alog10(4260.)-23. 
        else if (filter(1:1).EQ.'V') then
           lambda=5500
           const=alog10(3640.)-23. 
        else if (filter(1:1).EQ.'R') then 
           lambda=6400 
           const=alog10(3080.)-23. 
        else if (filter(1:1).EQ.'I') then 
           lambda=7900 
           const=alog10(2550.)-23. 
        else if (filter(1:1).EQ.'J') then 
           lambda=12600.
           const=alog10(1600.)-23. 
        else if (filter(1:1).EQ.'H') then 
           lambda=16500. 
           const=alog10(1020.)-23. 
        else if (filter(1:1).EQ.'K') then 
           lambda=22200. 
           const=alog10(657.)-23. 
        endif
c lambda from Amstrongs to microns
        lambda = lambda/10000.
        a_band=(0.574/lambda**1.61-0.527/lambda**1.61/Rv)*av
        c=3.e10
        a=1.0
        frequency=c/lambda*1.e4
c       write (*,*) ' frequency av, a_band ',frequency,av,a_band 
        flux = 10.**(-0.4*(m_band -a_band)+const)*frequency
        err=10.**(-0.4*(m_band - m_band_err - a_band)+const)
     &      *frequency-flux
        write (*,*) ' freq., dummy_error, flux, fl_err =' 
        write (*,*) frequency, a, flux , err
        END
