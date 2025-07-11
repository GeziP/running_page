interface ISiteMetadataResult {
  siteTitle: string;
  siteUrl: string;
  description: string;
  logo: string;
  navLinks: {
    name: string;
    url: string;
    isInternal?: boolean;
  }[];
}

const data: ISiteMetadataResult = {
  siteTitle: 'Running Page',
  siteUrl: 'https://gezi-lucas.blogspot.com/',
  logo: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQTtc69JxHNcmN1ETpMUX4dozAgAN6iPjWalQ&usqp=CAU',
  description: 'Personal site and blog',
  navLinks: [
    {
      name: '🏃‍♂️ 专业分析',
      url: '/professional-analysis',
      isInternal: true,
    },
    {
      name: 'Blog',
      url: 'https://gezi-lucas.blogspot.com/',
    },
    {
      name: 'About',
      url: 'https://github.com/yihong0618/running_page/blob/master/README-CN.md',
    },
  ],
};

export default data;
