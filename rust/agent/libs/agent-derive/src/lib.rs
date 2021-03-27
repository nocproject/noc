// ---------------------------------------------------------------------
// Agent derive macros
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput};

#[proc_macro_derive(Id)]
pub fn derive_id(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = input.ident;
    let expanded = quote! {
            impl Id for #name {
            fn get_id(&self) -> String {
                self.id.clone()
            }
        }
    };
    TokenStream::from(expanded)
}

#[proc_macro_derive(Repeatable)]
pub fn derive_repeatable(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = input.ident;
    let expanded = quote! {
            impl Repeatable for #name {
            fn get_interval(&self) -> u64 {
                self.interval
            }
        }
    };
    TokenStream::from(expanded)
}
