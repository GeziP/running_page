import { Link } from 'react-router-dom';
import useSiteMetadata from '@/hooks/useSiteMetadata';

const Header = () => {
  const { logo, siteUrl, navLinks } = useSiteMetadata();

  return (
    <>
      <nav className="mt-12 flex w-full items-center justify-between pl-6 lg:px-16">
        <div className="w-1/4">
          <Link to={siteUrl}>
            <picture>
              <img className="h-16 w-16 rounded-full" alt="logo" src={logo} />
            </picture>
          </Link>
        </div>
        <div className="w-3/4 text-right">
          {navLinks.map((n, i) => (
            n.isInternal ? (
              <Link
                key={i}
                to={n.url}
                className="mr-3 text-lg lg:mr-4 lg:text-base hover:text-blue-600 transition-colors"
              >
                {n.name}
              </Link>
            ) : (
              <a
                key={i}
                href={n.url}
                className="mr-3 text-lg lg:mr-4 lg:text-base hover:text-blue-600 transition-colors"
                target="_blank"
                rel="noopener noreferrer"
              >
                {n.name}
              </a>
            )
          ))}
        </div>
      </nav>
    </>
  );
};

export default Header;
